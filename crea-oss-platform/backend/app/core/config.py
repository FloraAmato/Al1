"""
Application configuration using Pydantic settings.
Loads configuration from environment variables.
"""
from typing import Literal, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    app_name: str = "CREA OSS Platform"
    app_version: str = "0.1.0"
    debug: bool = Field(default=False, validation_alias="DEBUG")
    environment: Literal["development", "staging", "production"] = "development"

    # API
    api_v1_prefix: str = "/api/v1"
    allowed_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"]
    )

    # Database
    database_url: str = Field(
        default="postgresql://crea:crea@localhost:5432/crea_db",
        validation_alias="DATABASE_URL"
    )
    database_echo: bool = False

    # Redis
    redis_host: str = Field(default="localhost", validation_alias="REDIS_HOST")
    redis_port: int = Field(default=6379, validation_alias="REDIS_PORT")
    redis_db: int = Field(default=0, validation_alias="REDIS_DB")
    redis_password: Optional[str] = Field(default=None, validation_alias="REDIS_PASSWORD")

    @property
    def redis_url(self) -> str:
        """Construct Redis URL from components."""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    # Celery
    celery_broker_url: Optional[str] = None
    celery_result_backend: Optional[str] = None

    @field_validator("celery_broker_url", mode="before")
    @classmethod
    def set_celery_broker(cls, v: Optional[str], info) -> str:
        """Default celery broker to redis_url if not set."""
        if v:
            return v
        # Access other values through info.data
        redis_host = info.data.get("redis_host", "localhost")
        redis_port = info.data.get("redis_port", 6379)
        redis_password = info.data.get("redis_password")
        if redis_password:
            return f"redis://:{redis_password}@{redis_host}:{redis_port}/1"
        return f"redis://{redis_host}:{redis_port}/1"

    @field_validator("celery_result_backend", mode="before")
    @classmethod
    def set_celery_backend(cls, v: Optional[str], info) -> str:
        """Default celery result backend to redis_url if not set."""
        if v:
            return v
        redis_host = info.data.get("redis_host", "localhost")
        redis_port = info.data.get("redis_port", 6379)
        redis_password = info.data.get("redis_password")
        if redis_password:
            return f"redis://:{redis_password}@{redis_host}:{redis_port}/2"
        return f"redis://{redis_host}:{redis_port}/2"

    # Vector Database (Qdrant)
    vector_db_type: Literal["qdrant", "chroma", "pgvector"] = "qdrant"
    qdrant_url: str = Field(default="http://localhost:6333", validation_alias="QDRANT_URL")
    qdrant_api_key: Optional[str] = Field(default=None, validation_alias="QDRANT_API_KEY")
    qdrant_collection_name: str = "crea_documents"

    # Embedding Model (open-source)
    embedding_model_name: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        validation_alias="EMBEDDING_MODEL"
    )
    embedding_device: str = "cpu"  # or "cuda" if GPU available
    embedding_batch_size: int = 32

    # LLM Configuration
    default_llm_backend: Literal["hf_local", "tgi", "vllm", "llamacpp"] = "hf_local"
    default_model_id: str = Field(
        default="mistralai/Mistral-7B-Instruct-v0.2",
        validation_alias="DEFAULT_MODEL_ID"
    )

    # HuggingFace Local Backend
    hf_device: str = "cpu"  # or "cuda"
    hf_load_in_8bit: bool = False
    hf_load_in_4bit: bool = False

    # Text Generation Inference (TGI) Backend
    tgi_url: Optional[str] = Field(default=None, validation_alias="TGI_URL")

    # vLLM Backend
    vllm_url: Optional[str] = Field(default=None, validation_alias="VLLM_URL")

    # llama.cpp Backend
    llamacpp_url: Optional[str] = Field(default=None, validation_alias="LLAMACPP_URL")

    # LLM Generation Parameters
    llm_max_new_tokens: int = 1024
    llm_temperature: float = 0.7
    llm_top_p: float = 0.9
    llm_top_k: int = 50

    # RAG Configuration
    rag_chunk_size: int = 512
    rag_chunk_overlap: int = 50
    rag_top_k: int = 5
    rag_score_threshold: float = 0.7

    # Cache Configuration
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 1 hour in seconds
    cache_max_size: int = 1000

    # Chat Configuration
    chat_history_ttl: int = 600  # 10 minutes
    chat_history_max_messages: int = 20

    # Security
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        validation_alias="SECRET_KEY"
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Fine-tuning Data Export
    export_data_dir: str = "./exports"

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"  # or "text"


# Global settings instance
settings = Settings()
