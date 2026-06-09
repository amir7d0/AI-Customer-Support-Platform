from __future__ import annotations

from datetime import datetime
from typing import Callable

from langchain_core.tools import tool

from .knowledge import KnowledgeBase
from .logging__ import log_ticket_event


# @tool
def create_internal_task(ticket_id: str, title: str, details: str, priority: str) -> str:
    """Create an internal action item for support or engineering teams."""
    task = {
        "ticket_id": ticket_id,
        "title": title,
        "details": details,
        "priority": priority,
        "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M"),
    }
    log_ticket_event(ticket_id, "internal_task_created", task)
    return f"Created task {title} for ticket {ticket_id}."


# @tool
def escalate_ticket(ticket_id: str, reason: str) -> str:
    """Flag a ticket for escalation and record the escalation reason."""
    event = {"ticket_id": ticket_id, "reason": reason, "escalated_at": datetime.now().strftime("%Y-%m-%dT%H:%M")}
    log_ticket_event(ticket_id, "ticket_escalated", event)
    return f"Ticket {ticket_id} escalated: {reason}"


def search_knowledge(query: str, knowledge_base: KnowledgeBase) -> str:
    """Retrieve relevant knowledge base information for a support ticket."""
    answer = knowledge_base.query(query)
    return f"Knowledge results for '{query}': {answer['answer']}\nSources: {answer['sources']}"


def build_support_tools(knowledge_base: KnowledgeBase) -> list:
    """Build list of tools for LLM binding."""
    # Create a dynamic search tool with knowledge base closure
    @tool
    def search_knowledge_base(query: str) -> str:
        """Retrieve relevant knowledge base information for a support ticket."""
        return search_knowledge(query, knowledge_base)
    
    return [
        create_internal_task,
        escalate_ticket,
        search_knowledge_base,
    ]

