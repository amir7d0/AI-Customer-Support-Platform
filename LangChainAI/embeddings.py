from __future__ import annotations

from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from langchain_openai import OpenAIEmbeddings
# from langchain_community.embeddings import HuggingFaceEmbeddings
from .config import settings


def get_embeddings():
    """
    Create an embedding instance using application settings.
    """
    provider = settings.EMBEDDING_PROVIDER
    
    if provider == "nvidia":
        return NVIDIAEmbeddings(
            model=settings.EMBEDDING_MODEL,
            api_key=settings.LLM_API_KEY,  # Using LLM API key for NVIDIA
            truncate="NONE",
        )
    elif provider == "openai":
        return OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            base_url=settings.EMBEDDING_BASE_URL,
            api_key=settings.LLM_API_KEY,  # Using LLM API key for OpenAI
        )
    # elif provider == "local":
    #     # Using HuggingFace embeddings for local option
    #     return HuggingFaceEmbeddings(
    #         model_name=settings.EMBEDDING_MODEL,
    #     )
    elif provider == "anthropic":
        # Anthropic doesn't provide a standard embedding model in LangChain
        # Fallback to OpenAI or raise error
        raise ValueError(
            "Anthropic provider not supported for embeddings. "
            "Use 'openai', 'nvidia', or 'local' instead."
        )
    else:
        # For langfuse/langsmith providers, these are tracking providers
        # not embedding providers, so we fallback to a default
        raise ValueError(
            f"Embedding provider '{provider}' not supported. "
            "Supported providers: 'nvidia', 'openai', 'local'"
        )