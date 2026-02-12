"""
Financial Intelligence Platform - Configuration Settings

Configuration management using environment variables and Pydantic settings.
Supports development, staging, and production environments.
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic import BaseSettings, Field


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

