from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .config import resolve_package_path, settings


class TicketMemoryManager:
    """Manages ticket history with JSON-based persistent storage."""
    
    def __init__(self, storage_file: str | Path | None = None) -> None:
        self.storage_file = Path(storage_file) if storage_file else resolve_package_path(settings.DATABASE_DIR) / "ticket_archive.json"
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)
        self._store: dict[str, Any] = {}
        self._memory_buffer: list[str] = []
        self._load_store()

    def _load_store(self) -> None:
        if self.storage_file.exists():
            self._store = json.loads(self.storage_file.read_text(encoding="utf-8"))
        else:
            self._store = {}

    def _write_store(self) -> None:
        self.storage_file.write_text(json.dumps(self._store, indent=2, ensure_ascii=False), encoding="utf-8")

    def add_ticket_summary(self, ticket_id: str, summary: str) -> None:
        """Add a ticket summary to persistent storage."""
        self._store[ticket_id] = {
            "summary": summary,
            "updated_at": datetime.utcnow().isoformat() + "Z",
        }
        self._write_store()

    def get_recent_summaries(self, limit: int = 5) -> list[dict[str, str]]:
        """Get recent ticket summaries."""
        summaries = [
            {"ticket_id": ticket_id, **metadata}
            for ticket_id, metadata in self._store.items()
        ]
        return sorted(summaries, key=lambda item: item["updated_at"], reverse=True)[:limit]

    def search_persistent_history(self, query: str, limit: int = 3) -> list[dict[str, str]]:
        """Search ticket history by query string."""
        query_lower = query.lower()
        matches = [
            {"ticket_id": ticket_id, **metadata}
            for ticket_id, metadata in self._store.items()
            if query_lower in metadata.get("summary", "").lower()
        ]
        return matches[:limit]

    def add_memory(self, ticket_text: str) -> None:
        """Add ticket text to in-memory buffer."""
        self._memory_buffer.append(ticket_text)
        # Keep last 10 items
        if len(self._memory_buffer) > 10:
            self._memory_buffer.pop(0)

    def get_memory_buffer(self) -> str:
        """Get concatenated memory buffer."""
        return "\n---\n".join(self._memory_buffer)

