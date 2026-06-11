from __future__ import annotations

from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from langchain_openai import OpenAIEmbeddings

from .config import settings


def get_embeddings():
    provider = settings.EMBEDDING_PROVIDER

    if provider == "nvidia":
        return NVIDIAEmbeddings(
            model=settings.EMBEDDING_MODEL,
            api_key=settings.LLM_API_KEY or None,
            truncate="NONE",
        )
    if provider == "openai":
        return OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            base_url=settings.EMBEDDING_BASE_URL,
            api_key=settings.LLM_API_KEY or None,
        )
    if provider == "anthropic":
        raise ValueError(
            "Anthropic provider is not supported for embeddings. Use 'openai', 'nvidia', or 'local'. \n You can implement it yourself by subclassing the BaseEmbeddings class from langchain and implementing the embed_documents and embed_query methods using the Anthropic API. \n If you want, you can add it to embeddings.py! ;) "
        )

    raise ValueError(
        f"Embedding provider '{provider}' is not supported. Supported providers: 'nvidia', 'openai', 'local'."
    )
