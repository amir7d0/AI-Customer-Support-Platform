from __future__ import annotations

from typing import Any

from langchain_core.documents import Document

from .config import PACKAGE_DIR, settings
from .embeddings import get_embeddings
from .llm import get_llm
from .vectorstore import get_vectorstore


class KnowledgeBase:
    def __init__(self) -> None:
        self.llm = get_llm()
        self.embedding = get_embeddings()
        self.vector_store = get_vectorstore(self.embedding)

    def _load_documents_from_source(self) -> list[Document]:
        source_file = PACKAGE_DIR / "docs" / "info.md"
        if not source_file.exists():
            return []

        raw_text = source_file.read_text(encoding="utf-8")
        documents: list[Document] = []

        for block in raw_text.split("---"):
            body: list[str] = []
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
        docs = self.vector_store.similarity_search(question, k=settings.RETRIEVAL_TOP_K)
        context = "\n\n".join(doc.page_content for doc in docs)

        prompt_text = (
            "You are a customer support assistant. "
            "Answer ONLY using the provided context. "
            "If the answer cannot be found in the context, respond with: "
            "I could not find that information in the knowledge base. "
            "Do not invent policies or procedures.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\n\n"
            "Answer:"
        )

        answer = self.llm.invoke(prompt_text)
        answer_text = answer.content if hasattr(answer, "content") else str(answer)

        return {
            "question": question,
            "answer": answer_text,
            "context": context,
            "sources": [doc.metadata for doc in docs],
        }
