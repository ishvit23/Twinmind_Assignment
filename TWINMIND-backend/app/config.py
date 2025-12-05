from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # -------------------------------------------------
    # API CONFIG
    # -------------------------------------------------
    API_TITLE: str = "TwinMind Second Brain"
    API_VERSION: str = "1.0.0"

    # -------------------------------------------------
    # DATABASE
    # -------------------------------------------------
    DATABASE_URL: str = ""

    # -------------------------------------------------
    # LLM CONFIG (OpenAI / OpenRouter)
    # -------------------------------------------------
    OPENROUTER_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    LLM_MODEL: str = "openai/gpt-3.5-turbo"

    # -------------------------------------------------
    # GEMINI (VISION OCR + RAG)
    # IMPORTANT: Your environment variable is GEMINI_API_KEY
    # -------------------------------------------------
    GEMINI_API_KEY: str | None = None     # <-- ADDED

    # Optional fallback field (not required but safe)
    GOOGLE_API_KEY: str | None = None     # <-- Allowed due to extra="allow"

    @property
    def gemini_key(self):
        """
        Use whichever environment variable Render provides.
        You use GEMINI_API_KEY, but this adds compatibility.
        """
        return self.GEMINI_API_KEY or self.GOOGLE_API_KEY

    # -------------------------------------------------
    # REDIS / CELERY
    # -------------------------------------------------
    REDIS_URL: str = ""

    # -------------------------------------------------
    # EMBEDDINGS (MiniLM)
    # -------------------------------------------------
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    # -------------------------------------------------
    # CHUNKING
    # -------------------------------------------------
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    # -------------------------------------------------
    # FILE UPLOADS
    # -------------------------------------------------
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    UPLOAD_DIR: str = "uploads"

    # -------------------------------------------------
    # TIMEZONE
    # -------------------------------------------------
    TIMEZONE: str = "UTC"

    # -------------------------------------------------
    # SECURITY
    # -------------------------------------------------
    SECRET_KEY: str = "change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # -------------------------------------------------
    # SERVER CONFIG
    # -------------------------------------------------
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # <-- Ensures Render custom variables don't break


@lru_cache()
def get_settings():
    return Settings()
