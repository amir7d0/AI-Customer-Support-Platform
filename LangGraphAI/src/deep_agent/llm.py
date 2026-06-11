from __future__ import annotations

from langchain.chat_models import init_chat_model

from .config import settings


def get_llm(*, temperature: float | None = None, streaming: bool | None = None):
    temperature = settings.LLM_TEMPERATURE if temperature is None else temperature
    streaming = settings.STREAMING if streaming is None else streaming

    return init_chat_model(
        model=settings.LLM_MODEL,
        api_key=settings.LLM_API_KEY or None,
        model_provider=settings.LLM_PROVIDER,
        temperature=temperature,
        base_url=settings.LLM_BASE_URL,
        streaming=streaming,
        timeout=settings.REQUEST_TIMEOUT,
        max_retries=settings.MAX_RETRIES,
    )
