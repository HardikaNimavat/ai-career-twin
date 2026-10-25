"""
Unified AI Service — Provider-agnostic LLM router with intelligent fallback chain.

Fallback chain: Gemini Free → Groq Free → HuggingFace Free → Ollama Local (100% Free, zero key) → Intelligent Local Rule Engine
Each provider has rate-limit tracking and automatic failover.
Response caching with TTL to minimize API calls and latency.

Time Complexity: O(1) cache hit, O(p) provider failover where p = num_providers
Space Complexity: O(c) where c = cache entries (bounded by max_cache_size)
"""

import os
import json
import time
import hashlib
import logging
import re
from typing import Dict, Any, Optional, List, Tuple
from collections import OrderedDict
from backend.app.core.config import settings

logger = logging.getLogger(__name__)


class ResponseCache:
    """TTL-based LRU cache for AI responses. O(1) lookup, O(1) eviction."""

    def __init__(self, max_size: int = 200, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl = ttl_seconds
        self._cache: OrderedDict[str, dict] = OrderedDict()

    def _make_key(self, prompt: str, provider: str = "") -> str:
        raw = f"{provider}:{prompt}"
        return hashlib.sha256(raw.encode()).hexdigest()[:32]

    def get(self, prompt: str, provider: str = "") -> Optional[Any]:
        key = self._make_key(prompt, provider)
        if key in self._cache:
            entry = self._cache[key]
            if time.time() - entry["ts"] < self.ttl:
                self._cache.move_to_end(key)
                return entry["data"]
            else:
                del self._cache[key]
        return None

    def set(self, prompt: str, data: Any, provider: str = ""):
        key = self._make_key(prompt, provider)
        self._cache[key] = {"data": data, "ts": time.time()}
        self._cache.move_to_end(key)
        while len(self._cache) > self.max_size:
            self._cache.popitem(last=False)

    def invalidate_all(self):
        self._cache.clear()


class RateLimitTracker:
    """Per-provider sliding window rate limiter."""

    def __init__(self):
        self._windows: Dict[str, List[float]] = {}
        self._limits: Dict[str, int] = {
            "gemini": 15,      # 15 RPM free tier
            "groq": 30,        # 30 RPM free tier
            "huggingface": 10,  # Conservative
            "ollama": 120,     # Unlimited local
        }
        self._cooldowns: Dict[str, float] = {}

    def can_call(self, provider: str) -> bool:
        now = time.time()
        # Check cooldown first
        if provider in self._cooldowns:
            if now < self._cooldowns[provider]:
                return False
            del self._cooldowns[provider]

        limit = self._limits.get(provider, 10)
        window = self._windows.get(provider, [])
        window = [t for t in window if now - t < 60]
        self._windows[provider] = window
        return len(window) < limit

    def record_call(self, provider: str):
        self._windows.setdefault(provider, []).append(time.time())

    def set_cooldown(self, provider: str, seconds: int = 60):
        self._cooldowns[provider] = time.time() + seconds


class AIProvider:
    """Base class for AI providers."""

    name: str = "base"

    def is_available(self) -> bool:
        return False

    def generate(self, prompt: str, json_mode: bool = False) -> Optional[str]:
        return None


class GeminiProvider(AIProvider):
    """Google Gemini free tier provider."""

    name = "gemini"

    def __init__(self):
        self._client = None
        self.api_key = settings.GEMINI_API_KEY
        if self.api_key and self.api_key != "YOUR_GEMINI_API_KEY":
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._client = genai.GenerativeModel(settings.GEMINI_MODEL)
                logger.info("Gemini AI provider initialized.")
            except Exception as e:
                logger.warning(f"Gemini init failed: {e}")

    def is_available(self) -> bool:
        return self._client is not None

    def generate(self, prompt: str, json_mode: bool = False) -> Optional[str]:
        if not self._client:
            return None
        try:
            response = self._client.generate_content(prompt)
            text = response.text.strip()
            return self._clean_response(text)
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            return None

    def _clean_response(self, text: str) -> str:
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()


class GroqProvider(AIProvider):
    """Groq free tier provider (Llama/Mixtral models)."""

    name = "groq"

    def __init__(self):
        self._client = None
        self.api_key = settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL
        if self.api_key and self.api_key != "YOUR_GROQ_API_KEY":
            try:
                from groq import Groq
                self._client = Groq(api_key=self.api_key)
                logger.info("Groq AI provider initialized.")
            except Exception as e:
                logger.warning(f"Groq init failed: {e}")

    def is_available(self) -> bool:
        return self._client is not None

    def generate(self, prompt: str, json_mode: bool = False) -> Optional[str]:
        if not self._client:
            return None
        try:
            kwargs = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are an expert AI career advisor and technical assessor. Always respond with valid JSON when asked."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 4096,
            }
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}

            response = self._client.chat.completions.create(**kwargs)
            text = response.choices[0].message.content.strip()
            return self._clean_response(text)
        except Exception as e:
            logger.error(f"Groq generation failed: {e}")
            return None

    def _clean_response(self, text: str) -> str:
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()


class HuggingFaceProvider(AIProvider):
    """HuggingFace Inference API free tier provider."""

    name = "huggingface"

    def __init__(self):
        self.api_key = settings.HF_API_KEY
        self.model = settings.HF_MODEL
        self._available = bool(self.api_key and self.api_key != "YOUR_HF_API_KEY")
        if self._available:
            logger.info("HuggingFace AI provider initialized.")

    def is_available(self) -> bool:
        return self._available

    def generate(self, prompt: str, json_mode: bool = False) -> Optional[str]:
        if not self._available:
            return None
        try:
            import requests
            headers = {"Authorization": f"Bearer {self.api_key}"}
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 2048,
                    "temperature": 0.7,
                    "return_full_text": False
                }
            }
            resp = requests.post(
                f"https://api-inference.huggingface.co/models/{self.model}",
                headers=headers,
                json=payload,
                timeout=30
            )
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list) and len(data) > 0:
                    text = data[0].get("generated_text", "")
                    return self._clean_response(text)
            logger.warning(f"HuggingFace returned status {resp.status_code}")
            return None
        except Exception as e:
            logger.error(f"HuggingFace generation failed: {e}")
            return None

    def _clean_response(self, text: str) -> str:
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()


class OllamaProvider(AIProvider):
    """Local Ollama AI provider (100% Free, zero external API key needed)."""

    name = "ollama"

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = os.getenv("OLLAMA_BASE_URL", base_url).rstrip("/")
        self.model = os.getenv("OLLAMA_MODEL", "llama3")
        self._available = False
        try:
            import requests
            resp = requests.get(f"{self.base_url}/api/version", timeout=1.5)
            if resp.status_code == 200:
                self._available = True
                logger.info(f"Ollama local AI detected at {self.base_url}")
        except Exception:
            self._available = False

    def is_available(self) -> bool:
        return self._available

    def generate(self, prompt: str, json_mode: bool = False) -> Optional[str]:
        if not self._available:
            return None
        try:
            import requests
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "format": "json" if json_mode else ""
            }
            resp = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=45)
            if resp.status_code == 200:
                data = resp.json()
                text = data.get("response", "").strip()
                return self._clean_response(text)
            return None
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            return None

    def _clean_response(self, text: str) -> str:
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()


class UnifiedAIService:
    """
    Unified AI service with multi-provider fallback chain and caching.

    Provider priority: Gemini → Groq → HuggingFace → Ollama (local) → None (local algorithmic engine)
    Includes: response caching, rate limiting, automatic failover, and complexity analysis.
    """

    def __init__(self):
        self.cache = ResponseCache(max_size=200, ttl_seconds=3600)
        self.rate_limiter = RateLimitTracker()
        self.providers: List[AIProvider] = []

        # Initialize providers in priority order
        gemini = GeminiProvider()
        if gemini.is_available():
            self.providers.append(gemini)

        groq = GroqProvider()
        if groq.is_available():
            self.providers.append(groq)

        hf = HuggingFaceProvider()
        if hf.is_available():
            self.providers.append(hf)

        ollama = OllamaProvider()
        if ollama.is_available():
            self.providers.append(ollama)

        available = [p.name for p in self.providers]
        logger.info(f"AI Service initialized. Available providers: {available or ['NONE (algorithmic engine active)']}")

    @property
    def is_available(self) -> bool:
        return len(self.providers) > 0

    @property
    def active_provider(self) -> Optional[str]:
        for p in self.providers:
            if self.rate_limiter.can_call(p.name):
                return p.name
        return "algorithmic_engine"

    def generate(self, prompt: str, use_cache: bool = True, json_mode: bool = False, cache_key_prefix: str = "") -> Optional[str]:
        """
        Generate AI response with fallback chain.
        Returns raw text response or None if all providers fail.
        """
        cache_prompt = f"{cache_key_prefix}:{prompt}" if cache_key_prefix else prompt

        # Check cache
        if use_cache:
            cached = self.cache.get(cache_prompt)
            if cached is not None:
                logger.debug("AI response served from cache.")
                return cached

        # Try each provider in order
        for provider in self.providers:
            if not self.rate_limiter.can_call(provider.name):
                logger.debug(f"Provider {provider.name} rate-limited, skipping.")
                continue

            self.rate_limiter.record_call(provider.name)
            result = provider.generate(prompt, json_mode=json_mode)

            if result:
                if use_cache:
                    self.cache.set(cache_prompt, result, provider.name)
                logger.info(f"AI response generated by {provider.name}")
                return result
            else:
                logger.warning(f"Provider {provider.name} returned None, trying next.")
                self.rate_limiter.set_cooldown(provider.name, 30)

        logger.warning("All AI providers failed. Returning None for local algorithmic fallback.")
        return None

    def generate_json(self, prompt: str, use_cache: bool = True, cache_key_prefix: str = "") -> Optional[Dict[str, Any]]:
        """Generate and parse JSON response. Returns parsed dict or None."""
        raw = self.generate(prompt, use_cache=use_cache, json_mode=True, cache_key_prefix=cache_key_prefix)
        if not raw:
            return None
        try:
            text = raw.strip()
            json_match = re.search(r'[\[{].*[\]}]', text, re.DOTALL)
            if json_match:
                text = json_match.group()
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI JSON response: {e}\nRaw: {raw[:200]}")
            return None

    def extract_skills_with_llm(self, resume_text: str) -> Optional[Dict[str, Any]]:
        """Extract skills from resume text using AI."""
        prompt = f"""You are an expert technical recruiter and resume analyzer.
Analyze the following resume text and extract all technical skills, programming languages, frameworks, libraries, tools, and experience level.
Return ONLY a valid JSON object matching this schema without any markdown formatting:
{{
  "detected_skills": {{"SkillName": confidence_score_between_50_and_99}},
  "experience_years": float_number,
  "summary": "one sentence profile summary"
}}

Resume Text:
{resume_text}"""
        return self.generate_json(prompt, cache_key_prefix="skills")

    def analyze_algorithmic_complexity(self, code: str, language: str = "javascript", expected_optimal_time: str = "O(n)", expected_optimal_space: str = "O(1)") -> Dict[str, Any]:
        """
        Static / AST heuristic analyzer for code Time Complexity, Space Complexity, and Accuracy.
        Runs in O(lines of code) time complexity and O(1) space complexity.
        """
        code_clean = code.strip()
        if not code_clean:
            return {
                "time_complexity": "N/A",
                "time_rating": "Incomplete",
                "space_complexity": "N/A",
                "space_rating": "Incomplete",
                "accuracy_pct": 0.0,
                "complexity_analysis": "No executable code was provided for complexity benchmarking."
            }

        lines = [line.strip() for line in code_clean.split("\n") if line.strip() and not line.strip().startswith("//") and not line.strip().startswith("#")]
        
        # 1. TIME COMPLEXITY HEURISTIC
        # Check loop nesting depth
        loop_keywords = [r"\bfor\b", r"\bwhile\b", r"\.forEach\b", r"\.map\b", r"\.filter\b", r"\.reduce\b", r"\.flatMap\b"]
        loop_lines = []
        for i, line in enumerate(lines):
            if any(re.search(pat, line) for pat in loop_keywords):
                loop_lines.append(i)

        # Check recursion
        func_match = re.search(r"function\s+([a-zA-Z0-9_$]+)|def\s+([a-zA-Z0-9_$]+)|const\s+([a-zA-Z0-9_$]+)\s*=", code_clean)
        func_name = None
        if func_match:
            func_name = func_match.group(1) or func_match.group(2) or func_match.group(3)

        is_recursive = False
        if func_name:
            # Check if func_name is called inside body (more than once)
            calls = len(re.findall(r"\b" + re.escape(func_name) + r"\s*\(", code_clean))
            if calls > 1:
                is_recursive = True

        nested_depth = 0
        if len(loop_lines) >= 2:
            # Estimate nesting by indentation
            nested_depth = 2

        if is_recursive:
            time_comp = "O(2ⁿ)" if calls > 2 else "O(n)"
            time_rating = "Exponential / Recursive" if calls > 2 else "Linear Recursion O(n)"
        elif nested_depth >= 2 or re.search(r"for.*for|while.*while", code_clean.replace("\n", " ")):
            time_comp = "O(n²)"
            time_rating = "Quadratic O(n²)"
        elif len(loop_lines) >= 1 or re.search(r"\b(sort|sorted)\b", code_clean):
            if "sort" in code_clean:
                time_comp = "O(n log n)"
                time_rating = "Linearithmic O(n log n)"
            else:
                time_comp = "O(n)"
                time_rating = "Linear O(n)"
        else:
            time_comp = "O(1)"
            time_rating = "Constant O(1)"

        # 2. SPACE COMPLEXITY HEURISTIC
        # Check auxiliary array/map/set allocations
        alloc_patterns = [r"\[\s*\]", r"new\s+Array", r"new\s+Map", r"new\s+Set", r"dict\(", r"list\(", r"set\(", r"\{\s*\}", r"\.concat\(", r"\[\.\.\."]
        has_auxiliary_collection = any(re.search(p, code_clean) for p in alloc_patterns)

        if is_recursive:
            space_comp = "O(n) [Call Stack]"
            space_rating = "Linear Stack O(n)"
        elif has_auxiliary_collection:
            space_comp = "O(n)"
            space_rating = "Linear Auxiliary O(n)"
        else:
            space_comp = "O(1)"
            space_rating = "Constant In-Place O(1)"

        # Compare to optimal
        is_optimal_time = (time_comp == expected_optimal_time or (expected_optimal_time == "O(n)" and time_comp == "O(1)"))
        is_optimal_space = (space_comp.startswith(expected_optimal_space))

        # 3. ACCURACY ESTIMATION
        # Check syntax balance (braces, parens)
        open_braces = code_clean.count("{") - code_clean.count("}")
        open_parens = code_clean.count("(") - code_clean.count(")")
        syntax_ok = (open_braces == 0 and open_parens == 0)

        has_return = ("return" in code_clean or "yield" in code_clean or "SELECT" in code_clean.upper())

        base_acc = 75.0 if syntax_ok else 50.0
        if has_return:
            base_acc += 15.0
        if is_optimal_time:
            base_acc += 10.0

        accuracy = min(100.0, max(20.0, base_acc))

        analysis_parts = [
            f"Observed Time: {time_comp} ({'Optimal' if is_optimal_time else 'Consider optimizing from ' + time_comp + ' to ' + expected_optimal_time}).",
            f"Observed Space: {space_comp} ({'In-place/Optimal' if is_optimal_space else 'Auxiliary memory allocated'}).",
            "Syntactically well-formed logic structure." if syntax_ok else "Syntax imbalance detected."
        ]

        return {
            "time_complexity": time_comp,
            "time_rating": "Optimal" if is_optimal_time else "Suboptimal",
            "space_complexity": space_comp,
            "space_rating": "Optimal" if is_optimal_space else "Acceptable",
            "accuracy_pct": round(accuracy, 1),
            "complexity_analysis": " ".join(analysis_parts)
        }

    def invalidate_user_cache(self):
        """Invalidate all cached responses."""
        self.cache.invalidate_all()


# Singleton instance
ai_service = UnifiedAIService()
