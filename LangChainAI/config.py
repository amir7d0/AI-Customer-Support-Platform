from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent


def resolve_package_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return PACKAGE_DIR / candidate

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    APP_NAME: str = "ai-customer-support"
    APP_ENV: Literal["development", "staging", "production"] = "development"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # LLM
    LLM_PROVIDER: Literal["local", "openai", "anthropic", "nvidia"] = "nvidia"
    LLM_MODEL: str
    LLM_API_KEY: str
    LLM_BASE_URL: str | None = None
    LLM_TEMPERATURE: float = Field(default=0.2, ge=0.0, le=2.0)
    STREAMING: bool = True

    # Embeddings
    EMBEDDING_PROVIDER: Literal["local", "openai", "anthropic", "nvidia"] = "nvidia"
    EMBEDDING_MODEL: str
    EMBEDDING_BASE_URL: str

    # Vector Stores
    VECTOR_STORE_PROVIDER: Literal["chroma", "qdrant"] = "chroma"
    VECTOR_STORE_BASE_URL: str

    # Tracking
    TRACKING_PROVIDER: Literal["langfuse", "langsmith"] = "langfuse"
    TRACKING_MODEL: str
    TRACKING_BASE_URL: str

    # Retrieval
    RETRIEVAL_TOP_K: int = Field(default=5, ge=1)
    RETRIEVAL_SCORE_THRESHOLD: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
    )

    # Escalation
    ESCALATION_CONFIDENCE_THRESHOLD: float = Field(
        default=0.75,
        ge=0.0,
        le=1.0,
    )

    # Database
    DATABASE_URL: str
    DATABASE_DIR: str

    # Observability
    ENABLE_TRACING: bool = False

    LANGSMITH_PROJECT: str | None = None
    LANGSMITH_API_KEY: str | None = None
    LANGSMITH_ENDPOINT: str | None = None

    LANGFUSE_PROJECT: str | None = None
    LANGFUSE_API_KEY: str | None = None
    LANGFUSE_HOST: str | None = None

    # Runtime
    MAX_RETRIES: int = Field(default=3, ge=0)
    REQUEST_TIMEOUT: int = Field(default=60, ge=1)

    # Human Review
    USE_HUMAN_REVIEW_CALLBACK: bool = False

    # Logging
    LOG_LEVEL: Literal[
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ] = "INFO"

    LOG_FORMAT: Literal[
        "json",
        "text",
    ] = "json"

    # Qdrant
    QDRANT_URL: str
    QDRANT_API_KEY: str | None = None
    QDRANT_COLLECTION_NAME: str
    QDRANT_PREFER_GRPC: bool = False

    # Chroma
    CHROMA_COLLECTION_NAME: str

settings = Settings()