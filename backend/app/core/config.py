"""
Financial Intelligence Platform - Configuration Settings

Configuration management using environment variables and Pydantic settings.
Supports development, staging, and production environments.
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import List, Optional

try:
    # pydantic v2 moved BaseSettings to the pydantic-settings package
    from pydantic_settings import BaseSettings
    from pydantic import Field
except Exception:
    # If pydantic-settings isn't available (CI/system without venv), provide a
    # lightweight fallback so the application and tests can import `settings`
    # without requiring installation of pydantic/pydantic-settings.
    def Field(default=None, *args, **kwargs):
        return default

    class BaseSettings:
        """
        Minimal fallback for Pydantic BaseSettings used only for tests/local
        execution when the real pydantic-settings package isn't installed.
        It populates instance attributes from class defaults.
        """

        def __init__(self, **kwargs):
            # copy class-level defaults to instance
            for name, value in list(self.__class__.__dict__.items()):
                if name.startswith("_"):
                    continue
                if callable(value):
                    continue
                setattr(self, name, value)

            # override with any provided kwargs
            for k, v in kwargs.items():
                setattr(self, k, v)

        def __repr__(self):
            return f"{self.__class__.__name__}({self.__dict__})"


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    
    # Application
    APP_NAME: str = "Financial Intelligence Platform"
    DEBUG: bool = True
    API_VERSION: str = "v1"
    
    # Database - Supports PostgreSQL, ClickHouse, and MySQL
    DATABASE_URL: str = "postgresql://financial_user:financial_secure_password@localhost:5432/financial_platform"
    MYSQL_URL: str = "mysql+pymysql://app_user:app_password@localhost:3306/financial_intel"
    CLICKHOUSE_URL: str = "clickhouse://localhost:8123"
    
    # Database Type Selection
    DATABASE_TYPE: str = "postgresql"  # Options: postgresql, mysql, clickhouse
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_DB: int = 0
    
    # Kafka
    KAFKA_URL: str = "localhost:9092"
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    
    # MinIO/S3
    MINIO_URL: str = "http://localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "financial-data"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 * 24  # 30 days
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    
    # Data Sources
    ALPHA_VANTAGE_API_KEY: Optional[str] = None
    NEWS_API_KEY: Optional[str] = None
    TWITTER_BEARER_TOKEN: Optional[str] = None
    
    # AI/NLP
    HF_TOKEN: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # File Storage
    UPLOAD_DIR: str = "/tmp/uploads"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    """
    return Settings()


# Global settings instance
settings = get_settings()

