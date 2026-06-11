from __future__ import annotations

from datetime import datetime

from langchain_core.tools import tool

from .knowledge import KnowledgeBase


def create_internal_task(ticket_id: str, title: str, details: str, priority: str) -> str:
    created_at = datetime.now().strftime("%Y-%m-%dT%H:%M")
    return f"Created task '{title}' for ticket {ticket_id} at {created_at}. Details: {details}"


def escalate_ticket(ticket_id: str, reason: str) -> str:
    escalated_at = datetime.now().strftime("%Y-%m-%dT%H:%M")
    return f"Ticket {ticket_id} escalated at {escalated_at}: {reason}"


def build_support_tools(knowledge_base: KnowledgeBase) -> list:
    @tool
    def search_knowledge(query: str) -> str:
        """Retrieve relevant knowledge base information for a support ticket."""
        answer = knowledge_base.query(query)
        return f"Knowledge results for '{query}': {answer['answer']}\nSources: {answer['sources']}"

    return [
        create_internal_task,
        escalate_ticket,
        search_knowledge,
    ]
