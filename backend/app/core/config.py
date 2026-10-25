import os
import logging
from typing import List

logger = logging.getLogger(__name__)

EXAMPLE_SECRET_KEYS = {
    "secret-key-ai-career-twin-indus-2026",
    "super-secret-key-change-this-in-production-ai-career-twin-2026",
    "replace_with_a_secure_random_secret_key_minimum_32_chars",
    "your_secret_key_here_change_in_production",
    "placeholder_secret_key",
    "change_me",
}

class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "AI Career Twin")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ai_career_twin.db")
    
    # AI & Cloud API Keys — Multi-provider fallback chain
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")
    HF_API_KEY: str = os.getenv("HF_API_KEY", "")
    HF_MODEL: str = os.getenv("HF_MODEL", "mistralai/Mixtral-8x7B-Instruct-v0.1")
    
    # GitHub
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    
    # File Upload
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    
    # Security: No insecure default secret key
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    
    # CORS: Read allowed origins from env (comma-separated), default to local origins
    _raw_origins: str = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000"
    )
    ALLOWED_ORIGINS: List[str] = [o.strip() for o in _raw_origins.split(",") if o.strip()]

    def validate_startup_secrets(self) -> None:
        """Enforces that production environments have a secure, non-example SECRET_KEY."""
        if self.APP_ENV == "production":
            if not self.SECRET_KEY or self.SECRET_KEY in EXAMPLE_SECRET_KEYS:
                raise ValueError(
                    "Production startup error: SECRET_KEY is missing or set to an insecure example value. "
                    "A strong, unique SECRET_KEY must be provided via environment variables in production."
                )

settings = Settings()
