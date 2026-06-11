from __future__ import annotations

from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from .config import resolve_package_path, settings


def get_vectorstore(embedding: Embeddings):
    if settings.VECTOR_STORE_PROVIDER == "chroma":
        chroma_dir = resolve_package_path("chroma_db")
        chroma_dir.mkdir(parents=True, exist_ok=True)
        return Chroma(
            collection_name=settings.CHROMA_COLLECTION_NAME,
            embedding_function=embedding,
            persist_directory=str(chroma_dir),
        )

    if settings.VECTOR_STORE_PROVIDER == "qdrant":
        client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
        )

        try:
            collections = client.get_collections()
            collection_names = [collection.name for collection in collections.collections]
            if settings.QDRANT_COLLECTION_NAME in collection_names:
                return QdrantVectorStore(
                    client=client,
                    collection_name=settings.QDRANT_COLLECTION_NAME,
                    embedding=embedding,
                )
        except Exception:
            pass

        return QdrantVectorStore.from_documents(
            documents=[],
            embedding=embedding,
            client=client,
            collection_name=settings.QDRANT_COLLECTION_NAME,
        )

    raise ValueError(
        "No vector store configured. Set VECTOR_STORE_PROVIDER to 'chroma' or 'qdrant'."
    )
