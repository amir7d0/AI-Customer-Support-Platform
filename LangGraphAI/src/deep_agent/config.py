from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PACKAGE_DIR = Path(__file__).resolve().parent


def resolve_package_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return PACKAGE_DIR / candidate


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PACKAGE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "ai-customer-support-langgraph"
    APP_ENV: Literal["development", "staging", "production"] = "development"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    LLM_PROVIDER: Literal["local", "openai", "anthropic", "nvidia"] = "nvidia"
    LLM_MODEL: str = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning"
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str | None = "https://integrate.api.nvidia.com/v1"
    LLM_TEMPERATURE: float = Field(default=0.2, ge=0.0, le=2.0)
    STREAMING: bool = False

    EMBEDDING_PROVIDER: Literal["local", "openai", "anthropic", "nvidia"] = "nvidia"
    EMBEDDING_MODEL: str = "nvidia/llama-nemotron-embed-1b-v2"
    EMBEDDING_BASE_URL: str = "https://integrate.api.nvidia.com/v1"

    VECTOR_STORE_PROVIDER: Literal["chroma", "qdrant"] = "chroma"
    VECTOR_STORE_BASE_URL: str = "http://localhost:8000"

    TRACKING_PROVIDER: Literal["langfuse", "langsmith"] = "langfuse"
    TRACKING_MODEL: str = ""
    TRACKING_BASE_URL: str = ""

    RETRIEVAL_TOP_K: int = Field(default=5, ge=1)
    RETRIEVAL_SCORE_THRESHOLD: float = Field(default=0.7, ge=0.0, le=1.0)

    ESCALATION_CONFIDENCE_THRESHOLD: float = Field(default=0.75, ge=0.0, le=1.0)

    DATABASE_URL: str = "sqlite:///support.db"
    DATABASE_DIR: str = "data"

    ENABLE_TRACING: bool = False

    LANGSMITH_PROJECT: str | None = None
    LANGSMITH_API_KEY: str | None = None
    LANGSMITH_ENDPOINT: str | None = None

    LANGFUSE_PROJECT: str | None = None
    LANGFUSE_API_KEY: str | None = None
    LANGFUSE_HOST: str | None = None

    MAX_RETRIES: int = Field(default=3, ge=0)
    REQUEST_TIMEOUT: int = Field(default=60, ge=1)

    USE_HUMAN_REVIEW_CALLBACK: bool = False

    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    LOG_FORMAT: Literal["json", "text"] = "json"

    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str | None = None
    QDRANT_COLLECTION_NAME: str = "ai_support_documents"
    QDRANT_PREFER_GRPC: bool = False

    CHROMA_COLLECTION_NAME: str = "ai_support_documents"


settings = Settings()
