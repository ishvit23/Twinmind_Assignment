from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # API Configuration
    API_TITLE: str = "TwinMind Second Brain"
    API_VERSION: str = "1.0.0"

    # Database (Render overrides this via environment)
    DATABASE_URL: str = ""

    # LLM / OpenRouter
    OPENROUTER_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    LLM_MODEL: str = "openai/gpt-3.5-turbo"

    # Redis / Celery
    REDIS_URL: str = ""

    # Embeddings (MATCH MiniLM)
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    # Chunking
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    # File Uploads
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    UPLOAD_DIR: str = "uploads"

    # Timezone
    TIMEZONE: str = "UTC"

    # Security
    SECRET_KEY: str = "change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Server default
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


@lru_cache()
def get_settings():
    return Settings()
