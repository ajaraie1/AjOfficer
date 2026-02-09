from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/igams"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # JWT
    jwt_secret: str = "your-super-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # OpenAI
    openai_api_key: str = ""
    
    # App
    app_name: str = "IGAMS"
    debug: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
