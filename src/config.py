"""
Configuration settings for Parallel AI Job Analyzer.
"""
import os
from typing import List, Dict
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment or defaults."""
    
    # API Keys
    GROQ_API_KEY: str = Field(default_factory=lambda: os.getenv("GROQ_API_KEY", ""))
    
    # Model Configuration
    DEFAULT_MODEL: str = Field(default_factory=lambda: os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"))
    FAST_MODEL: str = "openai/gpt-oss-20b"
    ACCURATE_MODEL: str = "openai/gpt-oss-120b"
    BACKUP_MODELS: List[str] = [
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "qwen/qwen3.6-27b",
        "groq/compound"
    ]
    
    # Concurrency & Performance
    DEFAULT_MAX_CONCURRENCY: int = 5
    MAX_ALLOWED_CONCURRENCY: int = 15
    REQUEST_TIMEOUT_SECONDS: float = 45.0
    MAX_RETRIES: int = 3
    RETRY_BASE_DELAY: float = 1.5
    
    # Scoring Weights (Normalized to 1.0)
    WEIGHT_SKILLS: float = 0.40
    WEIGHT_EXPERIENCE: float = 0.30
    WEIGHT_ATS_KEYWORDS: float = 0.15
    WEIGHT_DOMAIN_EDUCATION: float = 0.15
    
    # Output Thresholds
    HIGH_FIT_THRESHOLD: float = 80.0
    MEDIUM_FIT_THRESHOLD: float = 60.0
    
    # App Information
    APP_NAME: str = "Parallel AI Job Analyzer"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"

    model_config = {
        "case_sensitive": True,
        "extra": "ignore"
    }

# Global settings instance
settings = Settings()

