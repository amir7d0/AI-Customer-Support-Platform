from __future__ import annotations

import os
from .config import settings


def setup_tracking():
    """
    Setup tracing based on TRACKING_PROVIDER setting.
    Configures either LangSmith or LangFuse tracing for LangChain.
    """
    if not settings.ENABLE_TRACING:
        return
    
    provider = settings.TRACKING_PROVIDER
    
    if provider == "langsmith":
        # Setup LangSmith tracing
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_ENDPOINT"] = (
            settings.LANGSMITH_ENDPOINT 
            if hasattr(settings, 'LANGSMITH_ENDPOINT') and settings.LANGSMITH_ENDPOINT
            else "https://api.smith.langchain.com"
        )
        os.environ["LANGCHAIN_API_KEY"] = settings.LANGSMITH_API_KEY
        os.environ["LANGCHAIN_PROJECT"] = (
            settings.LANGSMITH_PROJECT 
            if settings.LANGSMITH_PROJECT 
            else settings.APP_NAME
        )
        
    elif provider == "langfuse":
        # Setup LangFuse tracing
        os.environ["LANGFUSE_SECRET_KEY"] = settings.LANGFUSE_API_KEY
        os.environ["LANGFUSE_PUBLIC_KEY"] = settings.LANGFUSE_API_KEY  # Assuming same key for simplicity
        os.environ["LANGFUSE_HOST"] = (
            settings.LANGFUSE_HOST 
            if hasattr(settings, 'LANGFUSE_HOST') and settings.LANGFUSE_HOST
            else "https://cloud.langfuse.com"
        )
    

def is_tracing_enabled() -> bool:
    """Check if tracing is enabled and properly configured."""
    if not settings.ENABLE_TRACING:
        return False
    
    provider = settings.TRACKING_PROVIDER
    
    if provider == "langsmith":
        return bool(settings.LANGSMITH_API_KEY)
    elif provider == "langfuse":
        return bool(settings.LANGFUSE_API_KEY)
    
    return False