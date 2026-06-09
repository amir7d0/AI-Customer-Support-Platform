
from langchain.chat_models import init_chat_model
from .config import settings


def get_llm(*, temperature: float | None = None, streaming: bool | None = None):
    """
    Create a LangChain chat model instance using application settings.
    """
    temperature = (temperature if temperature is not None else settings.LLM_TEMPERATURE)
    streaming = (streaming if streaming is not None else settings.STREAMING)

    return init_chat_model(
        model=settings.LLM_MODEL,
        api_key=settings.LLM_API_KEY,
        model_provider=settings.LLM_PROVIDER,
        temperature=temperature,
        base_url=settings.LLM_BASE_URL,
        streaming=streaming,
        timeout=settings.REQUEST_TIMEOUT,
        max_retries=settings.MAX_RETRIES,
    )
