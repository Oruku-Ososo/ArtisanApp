"""
Configuration Module for Bible Digital Twin

Production-grade configuration management with environment variables,
secrets management, and feature flags.
"""

import os
from typing import Optional, List, Dict, Any
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    APP_NAME: str = "Bible Digital Twin"
    APP_VERSION: str = "2.0.0"
    APP_ENV: str = Field(default="production", env="APP_ENV")
    DEBUG: bool = Field(default=False, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # API Configuration
    API_PREFIX: str = "/api/v2"
    CORS_ORIGINS: List[str] = ["*"]
    ALLOWED_HOSTS: List[str] = ["*"]
    MAX_REQUEST_SIZE: int = 10 * 1024 * 1024  # 10MB
    REQUEST_TIMEOUT: int = 30  # seconds
    
    # Database
    DATABASE_URL: str = Field(default="sqlite:///./bible_digital_twin.db", env="DATABASE_URL")
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_ECHO: bool = False
    
    # Redis Cache
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    CACHE_TTL: int = 3600  # 1 hour
    ENABLE_CACHE: bool = True
    
    # AI Models
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    NER_MODEL: str = "en_core_web_sm"
    TRANSFORMER_MODEL: str = "bert-base-uncased"
    MODEL_CACHE_DIR: str = "./models_cache"
    ENABLE_SEMANTIC_SEARCH: bool = True
    SEMANTIC_SEARCH_THRESHOLD: float = 0.5
    
    # Knowledge Graph
    KG_MAX_PATH_LENGTH: int = 10
    KG_ENABLE_INFERENCE: bool = True
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Security
    SECRET_KEY: str = Field(default="change-me-in-production", env="SECRET_KEY")
    API_KEY_HEADER: str = "X-API-Key"
    ENABLE_API_KEY_AUTH: bool = False
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60
    
    # Monitoring & Observability
    ENABLE_METRICS: bool = True
    ENABLE_TRACING: bool = False
    METRICS_ENDPOINT: str = "/metrics"
    HEALTH_CHECK_INTERVAL: int = 30
    
    # Performance
    ENABLE_COMPRESSION: bool = True
    COMPRESSION_LEVEL: int = 6
    WORKER_COUNT: int = 4
    THREADS_PER_WORKER: int = 2
    
    # Feature Flags
    FEATURE_ADVANCED_SEARCH: bool = True
    FEATURE_KNOWLEDGE_GRAPH: bool = True
    FEATURE_CROSS_REFERENCES: bool = True
    FEATURE_NER: bool = True
    FEATURE_ANALYTICS: bool = True
    FEATURE_EXPORT: bool = True
    FEATURE_BOOKMARKS: bool = True
    FEATURE_USER_PREFERENCES: bool = True
    
    # External Services
    NEO4J_URI: Optional[str] = Field(default=None, env="NEO4J_URI")
    NEO4J_USER: Optional[str] = Field(default=None, env="NEO4J_USER")
    NEO4J_PASSWORD: Optional[str] = Field(default=None, env="NEO4J_PASSWORD")
    
    # File Storage
    STORAGE_BACKEND: str = "local"  # local, s3, gcs
    S3_BUCKET: Optional[str] = Field(default=None, env="S3_BUCKET")
    S3_REGION: Optional[str] = Field(default=None, env="S3_REGION")
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    @field_validator('APP_ENV')
    @classmethod
    def validate_env(cls, v):
        allowed = ['development', 'staging', 'production', 'testing']
        if v not in allowed:
            raise ValueError(f'APP_ENV must be one of {allowed}')
        return v
    
    @field_validator('LOG_LEVEL')
    @classmethod
    def validate_log_level(cls, v):
        allowed = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v not in allowed:
            raise ValueError(f'LOG_LEVEL must be one of {allowed}')
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Convenience exports
settings = get_settings()
