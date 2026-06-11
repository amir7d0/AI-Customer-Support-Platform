from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from .config import resolve_package_path, settings
from .schemas import DraftResponse, TaskItem, TicketAnalysisResult, TicketMetadata


class DBManager:
    def __init__(self, db_path: str | Path | None = None) -> None:
        self.db_path = Path(db_path) if db_path else resolve_package_path(settings.DATABASE_DIR) / "support.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self) -> None:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tickets (
                ticket_id TEXT PRIMARY KEY,
                sender TEXT,
                subject TEXT,
                body TEXT,
                received_at TEXT,
                created_at TEXT
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS analyses (
                ticket_id TEXT,
                analysis_json TEXT,
                created_at TEXT,
                FOREIGN KEY(ticket_id) REFERENCES tickets(ticket_id)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS responses (
                ticket_id TEXT,
                response_json TEXT,
                created_at TEXT,
                FOREIGN KEY(ticket_id) REFERENCES tickets(ticket_id)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id TEXT,
                title TEXT,
                description TEXT,
                priority TEXT,
                created_at TEXT,
                FOREIGN KEY(ticket_id) REFERENCES tickets(ticket_id)
            )
            """
        )
        self.connection.commit()

    def save_ticket(self, ticket: TicketMetadata) -> None:
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO tickets (ticket_id, sender, subject, body, received_at, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (
                ticket.ticket_id,
                ticket.sender,
                ticket.subject,
                ticket.body,
                ticket.received_at.isoformat(),
                datetime.now().isoformat() + "Z",
            ),
        )
        self.connection.commit()

    def save_analysis(self, ticket_id: str, analysis: TicketAnalysisResult) -> None:
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO analyses (ticket_id, analysis_json, created_at) VALUES (?, ?, ?)",
            (
                ticket_id,
                json.dumps(analysis.model_dump(), ensure_ascii=False),
                datetime.now().isoformat() + "Z",
            ),
        )
        self.connection.commit()

    def save_response(self, ticket_id: str, response: DraftResponse) -> None:
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO responses (ticket_id, response_json, created_at) VALUES (?, ?, ?)",
            (
                ticket_id,
                json.dumps(response.model_dump(), ensure_ascii=False),
                datetime.now().isoformat() + "Z",
            ),
        )
        self.connection.commit()

    def save_task(self, ticket_id: str, task: TaskItem) -> None:
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO tasks (ticket_id, title, description, priority, created_at) VALUES (?, ?, ?, ?, ?)",
            (
                ticket_id,
                task.title,
                task.description,
                task.priority,
                datetime.now().isoformat() + "Z",
            ),
        )
        self.connection.commit()

    def find_recent_tickets(self, limit: int = 10) -> list[dict[str, Any]]:
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT ticket_id, sender, subject, received_at, created_at FROM tickets ORDER BY created_at DESC LIMIT ?",
            (limit,),
        )
        return [dict(row) for row in cursor.fetchall()]
