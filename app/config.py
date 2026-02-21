from pydantic_settings import BaseSettings
from functools import lru_cache
import os
import logging

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Location Safety RAG"
    DEBUG: bool = os.getenv("DEBUG", "False") == "True"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:password@localhost:5432/location_safety"
    )
    
    # Embeddings
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    
    # LLM - GROQ
    LLM_TYPE: str = "groq"
    LLM_MODEL: str = os.getenv("LLM_MODEL", "mixtral-8x7b-32768")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # RAG Parameters
    RAG_K_RETRIEVAL: int = 15
    RAG_DISTANCE_THRESHOLD: float = 0.3
    GEO_RADIUS_KM: float = 50.0
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def validate_groq_key(self) -> bool:
        """Validate Groq API key is set"""
        if not self.GROQ_API_KEY:
            raise ValueError(
                "❌ GROQ_API_KEY not set! Get free key from https://console.groq.com"
            )
        return True

@lru_cache()
def get_settings():
    settings = Settings()
    # Only validate in production if explicitly needed
    # Render sets env vars after startup sometimes
    try:
        if settings.ENVIRONMENT == "production":
            if not settings.GROQ_API_KEY:
                raise ValueError("GROQ_API_KEY required in production")
    except ValueError as e:
        logger.warning(f"Config warning: {e}")
    return settings
