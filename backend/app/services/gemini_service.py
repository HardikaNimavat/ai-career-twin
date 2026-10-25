import os
import json
import logging
from typing import Dict, Any, Optional
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL
        self._client = None
        
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._client = genai.GenerativeModel(self.model_name)
                logger.info("Google Gemini API configured successfully.")
            except Exception as e:
                logger.warning(f"Could not initialize Gemini Client: {e}")

    @property
    def is_available(self) -> bool:
        return self._client is not None

    def extract_skills_with_llm(self, resume_text: str) -> Optional[Dict[str, Any]]:
        if not self.is_available:
            return None
        
        prompt = f"""You are an expert technical recruiter and resume analyzer.
Analyze the following resume text and extract all technical skills, programming languages, frameworks, libraries, tools, and experience level.
Return ONLY a valid JSON object matching this schema without any markdown formatting:
{{
  "detected_skills": {{"SkillName": confidence_score_between_50_and_99}},
  "experience_years": float_number,
  "summary": "one sentence profile summary"
}}

Resume Text:
{resume_text}
"""
        try:
            response = self._client.generate_content(prompt)
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            data = json.loads(text.strip())
            return data
        except Exception as e:
            logger.error(f"Gemini skill extraction failed: {e}")
            return None

gemini_service = GeminiService()
