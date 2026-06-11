from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class TicketMetadata(BaseModel):
    ticket_id: str = Field(default_factory=lambda: str(uuid4()))
    sender: str
    subject: str | None = None
    body: str
    received_at: datetime = Field(default_factory=datetime.now)

    @classmethod
    def from_email(cls, raw_email: str) -> "TicketMetadata":
        sender = "unknown@example.com"
        subject = "General Support Request"
        body_lines: list[str] = []
        body_section = False

        for line in raw_email.splitlines():
            stripped = line.strip()
            if stripped.lower().startswith("from:"):
                sender = stripped.split(":", 1)[1].strip()
            elif stripped.lower().startswith("subject:"):
                subject = stripped.split(":", 1)[1].strip()
            elif stripped.lower().startswith("body:"):
                body_section = True
            elif body_section:
                body_lines.append(line)

        body = "\n".join(body_lines).strip() or raw_email.strip()
        return cls(sender=sender, subject=subject, body=body)


class TicketAnalysisResult(BaseModel):
    category: str
    priority: Literal["low", "medium", "high", "critical"]
    escalate: bool
    escalation_reason: str
    tasks: list[TaskItem]
    knowledge_queries: list[str]


class TaskItem(BaseModel):
    title: str
    description: str
    ticket_id: str
    priority: str


class DraftResponse(BaseModel):
    response: str
    follow_up_instructions: str


class TicketLogEntry(BaseModel):
    ticket_id: str
    analysis: TicketAnalysisResult
    response: DraftResponse
    created_at: datetime = Field(default_factory=datetime.now)
