from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # App
    APP_NAME: str = "Coupon Book Service"
    DEBUG: bool = True
    APP_VERSION: str = "2.0.0"
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str
    
    # JWT Security
    SECRET_KEY: str = "dev-secret-key-change-in-production-use-openssl-rand-hex-32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Concurrency
    LOCK_TIMEOUT_SECONDS: int = 300
    MAX_LOCK_RETRIES: int = 3
    
    # Code Generation
    CODE_GENERATION_CHARSET: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    MAX_COLLISION_RETRIES: int = 3
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
