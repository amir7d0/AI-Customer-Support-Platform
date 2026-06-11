from __future__ import annotations

from pathlib import Path

from langchain_qdrant import QdrantVectorStore
from langchain_chroma import Chroma
from qdrant_client import QdrantClient
from langchain_core.embeddings import Embeddings
from .config import settings
from .config import PACKAGE_DIR


def get_vectorstore(embedding: Embeddings):
    """
    Create a vectorstore instance using application settings.
    
    Args:
        embedding: The embedding function to use with the vectorstore
        
    Returns:
        A vectorstore instance (Chroma or Qdrant)
    """
    # Check if we should use Chroma
    if settings.CHROMA_COLLECTION_NAME:
        return Chroma(
            collection_name=settings.CHROMA_COLLECTION_NAME,
            embedding_function=embedding,
            persist_directory=str(PACKAGE_DIR / "chroma_db"),
        )
    
    # Check if we should use Qdrant
    if settings.QDRANT_COLLECTION_NAME:
        client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
        )
        
        # Check if collection already exists
        try:
            collections = client.get_collections()
            collection_names = [c.name for c in collections.collections]
            
            if settings.QDRANT_COLLECTION_NAME in collection_names:
                return QdrantVectorStore(
                    client=client,
                    collection_name=settings.QDRANT_COLLECTION_NAME,
                    embedding=embedding,
                )
        except Exception:
            # If we can't check collections, assume it doesn't exist
            pass
        
        # Create new collection
        return QdrantVectorStore.from_documents(
            documents=[],  # Empty initial documents, will be added later
            embedding=embedding,
            client=client,
            collection_name=settings.QDRANT_COLLECTION_NAME,
        )
    
    # If neither is configured, raise an error
    raise ValueError(
        "No vector store configured. Please set either CHROMA_COLLECTION_NAME "
        "or QDRANT_COLLECTION_NAME in your configuration."
    )