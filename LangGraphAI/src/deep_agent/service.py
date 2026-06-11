from __future__ import annotations

from .db import DBManager
from .knowledge import KnowledgeBase
from .memory_manager import TicketMemoryManager
from .nodes import SupportTicketWorkflow
from .tools import build_support_tools


def create_support_service() -> SupportTicketWorkflow:
    memory_manager = TicketMemoryManager()
    knowledge_base = KnowledgeBase()
    db_manager = DBManager()
    return SupportTicketWorkflow(
        memory_manager=memory_manager,
        knowledge_base=knowledge_base,
        db_manager=db_manager,
    )


def create_support_tools():
    return build_support_tools(KnowledgeBase())
