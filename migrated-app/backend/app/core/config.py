"""
Application configuration settings using Pydantic Settings.
"""
from typing import List, Optional
from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"
    )

    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "CREA2 - Fair Division Platform"
    VERSION: str = "2.0.0"
    DESCRIPTION: str = "A platform for fair division of goods using optimization algorithms"

    # CORS Settings
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    # Database Settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "crea_user"
    POSTGRES_PASSWORD: str = "crea_password"
    POSTGRES_DB: str = "crea_db"
    DATABASE_URL: Optional[str] = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v, info):
        if v:
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=info.data.get("POSTGRES_USER"),
            password=info.data.get("POSTGRES_PASSWORD"),
            host=info.data.get("POSTGRES_SERVER"),
            port=info.data.get("POSTGRES_PORT"),
            path=info.data.get("POSTGRES_DB"),
        ).unicode_string()

    # Redis Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URL: Optional[str] = None

    @field_validator("REDIS_URL", mode="before")
    @classmethod
    def assemble_redis_connection(cls, v, info):
        if v:
            return v
        return f"redis://{info.data.get('REDIS_HOST')}:{info.data.get('REDIS_PORT')}/{info.data.get('REDIS_DB')}"

    # Security Settings
    SECRET_KEY: str = "change-this-to-a-secure-random-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days

    # Email Settings
    MAIL_USERNAME: Optional[str] = None
    MAIL_PASSWORD: Optional[str] = None
    MAIL_FROM: str = "noreply@crea.eu"
    MAIL_FROM_NAME: str = "CREA2 Platform"
    MAIL_SERVER: str = "smtp.mailjet.com"
    MAIL_PORT: int = 587
    MAIL_TLS: bool = True
    MAILJET_API_KEY: Optional[str] = None
    MAILJET_API_SECRET: Optional[str] = None

    # Blockchain Settings
    BLOCKCHAIN_API_URL: str = "https://chain.scan2project.org"
    BLOCKCHAIN_USERNAME: Optional[str] = None
    BLOCKCHAIN_PASSWORD: Optional[str] = None
    BLOCKCHAIN_ENABLED: bool = False

    # LLM Settings (Optional)
    LLM_ENABLED: bool = False
    OPENAI_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-4"
    LLM_SERVICE_URL: Optional[str] = None

    # Celery Settings
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    @field_validator("CELERY_BROKER_URL", mode="before")
    @classmethod
    def assemble_celery_broker(cls, v, info):
        if v:
            return v
        return info.data.get("REDIS_URL")

    @field_validator("CELERY_RESULT_BACKEND", mode="before")
    @classmethod
    def assemble_celery_backend(cls, v, info):
        if v:
            return v
        return info.data.get("REDIS_URL")

    # Superuser Settings
    FIRST_SUPERUSER_EMAIL: str = "admin@crea.eu"
    FIRST_SUPERUSER_PASSWORD: str = "changethis"
    FIRST_SUPERUSER_NAME: str = "Admin"
    FIRST_SUPERUSER_SURNAME: str = "User"

    # Optimization Settings
    OPTIMIZATION_TIMEOUT: int = 300  # 5 minutes
    OPTIMIZATION_ASYNC_THRESHOLD: int = 10  # Run async if more than 10 agents or goods

    # Frontend URL
    FRONTEND_URL: str = "http://localhost:3000"


# Create settings instance
settings = Settings()
