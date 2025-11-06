import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Language Learning Center API"
    VERSION: str = "1.0.0"
    
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    DATABASE_URL: str
    STORAGE_PATH: str = "/tmp/persistent_storage"
    NARAKEET: str
    REDIS_URL: str
    
    SUPER_ADMIN_EMAIL: str
    SUPER_ADMIN_PASSWORD: str
    ADMIN_BYPASS_KEY: str = "zehnly_admin_bypass_2024"
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields from .env


settings = Settings()