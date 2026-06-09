from __future__ import annotations

from pathlib import Path
from typing import Any

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.embeddings import Embeddings
from .llm import get_llm
from .config import settings
from .embeddings import get_embeddings
from .vectorstore import get_vectorstore


class KnowledgeBase:
    """Knowledge base for RAG using Qdrant/Chroma vector storage."""

    def __init__(self) -> None:
        self.llm = get_llm()
        self.embedding = get_embeddings()
        self.vector_store = get_vectorstore(self.embedding)

    def _load_documents_from_source(self) -> list[Document]:
        """Load documents from markdown source file."""
        source_file = Path(__file__).resolve().parent / "docs" / "info.md"
        if not source_file.exists():
            print("./docs/info.md does not exist!!!")
            return

        raw_text = source_file.read_text(encoding="utf-8")
        documents = []
        for block in raw_text.split("---"):

            body = []
            metadata: dict[str, str] = {}
            for line in block.strip().splitlines():
                stripped = line.strip()
                if stripped.startswith("category:"):
                    metadata["category"] = stripped.split(":", 1)[1].strip()
                elif stripped.startswith("title:"):
                    metadata["title"] = stripped.split(":", 1)[1].strip()
                elif stripped:
                    body.append(line)
            
            if "\n".join(body).strip() == "":
                continue

            documents.append(
                Document(
                    page_content="\n".join(body).strip(),
                    metadata={
                        "title": metadata.get("title", "unknown"),
                        "category": metadata.get("category", "unknown"),
                    },
                )
            )

        return documents

    def query(self, question: str) -> dict[str, Any]:
        """Query knowledge base using retriever."""
        # Retrieve source documents
        docs = self.vector_store.similarity_search(
            question, k=settings.RETRIEVAL_TOP_K)

        # Format retrieved documents
        context = "\n\n".join(doc.page_content for doc in docs)
    
        # Create prompt and invoke LLM directly
        prompt_text = (
            f"You are a customer support assistant."
            f"Answer ONLY using the provided context."
            f"If the answer cannot be found in the context, respond with:"
            f"I could not find that information in the knowledge base."
            f"Do not invent policies or procedures."
            f"Context:\n{context}\n\n"
            f"Question: {question}\n\n"
            f"Answer:"
        )

        answer = self.llm.invoke(prompt_text)
        answer_text = (answer.content if hasattr(answer, "content") else str(answer))

        return {
            "question": question,
            "answer": answer_text,
            "context": context,
            "sources": [doc.metadata for doc in docs],
        }
