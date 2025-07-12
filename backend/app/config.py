"""
Configuration management for the Agno chatbot application.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    app_name: str = "Agno Bot"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    
    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # API Keys
    google_gemini_api_key: str = Field(default="AIzaSyC4rm2apYeyP3_SbDWde2fZUjgtSRiVxqo", env="GEMINI_API_KEY")
    zep_api_key: str = Field(default="z_1dWlkIjoiNGZmYzY0YWUtOGVjMC00MDZhLTliNzQtYzFiYTk3MWUwOGE0In0.bYSkQGYuRLUWZFI36aufjKeHC0eCivYnoMNwy7BHxFSmlF93jDh75sbEzOto1bk4gpZfowutc8cRZlrY8N26Zw", env="ZEP_API_KEY")
    mem0_api_key: str = Field(default="m0-NVMJ3xOTkp80sy9jlcvplcufEb6OlCUe9u8EdOKD", env="MEM0_API_KEY")
    
    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # Memory Systems
    zep_base_url: str = Field(default="https://api.zep.ai", env="ZEP_BASE_URL")
    mem0_base_url: str = Field(default="https://api.mem0.ai", env="MEM0_BASE_URL")
    
    # Memory Configuration
    zep_session_ttl: int = Field(default=3600, env="ZEP_SESSION_TTL")  # 1 hour
    mem0_fact_ttl: int = Field(default=86400, env="MEM0_FACT_TTL")  # 24 hours
    max_memory_context: int = Field(default=1000, env="MAX_MEMORY_CONTEXT")
    
    # Gemini Configuration
    gemini_model: str = Field(default="gemini-1.5-pro")
    gemini_max_tokens: int = Field(default=2048, env="GEMINI_MAX_TOKENS")
    gemini_temperature: float = Field(default=0.7, env="GEMINI_TEMPERATURE")
    
    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    
    # CORS
    cors_origins: list[str] = Field(default=["http://localhost:3000"], env="CORS_ORIGINS")
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings


def validate_environment() -> bool:
    """Validate that all required environment variables are set."""
    required_vars = [
        "GEMINI_API_KEY",
        "ZEP_API_KEY", 
        "MEM0_API_KEY",
        "DATABASE_URL",
        "SECRET_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("Using default API keys and placeholder values for testing.")
        # Set default values for testing
        os.environ.setdefault("GEMINI_API_KEY", "AIzaSyC4rm2apYeyP3_SbDWde2fZUjgtSRiVxqo")
        os.environ.setdefault("ZEP_API_KEY", "z_1dWlkIjoiNGZmYzY0YWUtOGVjMC00MDZhLTliNzQtYzFiYTk3MWUwOGE0In0.bYSkQGYuRLUWZFI36aufjKeHC0eCivYnoMNwy7BHxFSmlF93jDh75sbEzOto1bk4gpZfowutc8cRZlrY8N26Zw")
        os.environ.setdefault("MEM0_API_KEY", "m0-NVMJ3xOTkp80sy9jlcvplcufEb6OlCUe9u8EdOKD")
        os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
        os.environ.setdefault("SECRET_KEY", "test_secret_key_for_development_only")
        return True
    
    print("✅ All required environment variables are set")
    return True 