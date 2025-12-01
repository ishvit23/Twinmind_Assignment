from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # API Configuration
    API_TITLE: str = "TwinMind Second Brain"
    API_VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = "postgresql://twinmind_db_user:x6zydrD2iC9J6J20vKrBwgqetlCVtJzU@dpg-d4mp0j2li9vc73f1a8t0-a/twinmind_db"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "twinmind_db"
    
    # LLM / OpenRouter
    OPENROUTER_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    LLM_MODEL: str = "openai/gpt-3.5-turbo"  # or any model from OpenRouter
    
    # Redis / Celery
    REDIS_URL: str = "redis://localhost:6379"
    
    # Embedding Model
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSION: int = 1536
    
    # Chunk Configuration
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # File Upload
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    UPLOAD_DIR: str = "uploads"
    
    # Temporal
    TIMEZONE: str = "UTC"
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields from .env

@lru_cache()
def get_settings():
    return Settings()
