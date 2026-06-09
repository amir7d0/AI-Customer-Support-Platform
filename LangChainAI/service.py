from __future__ import annotations

from .chains import SupportTicketWorkflow
from .db import DBManager
from .knowledge import KnowledgeBase
from .logging__ import configure_logger
from .memory_manager import TicketMemoryManager
from .tools import build_support_tools
from .tracking import setup_tracking


def create_support_service() -> tuple[SupportTicketWorkflow, list]:
    setup_tracking()
    logger = configure_logger()
    logger.info("Starting AI Customer Support Platform service")

    memory_manager = TicketMemoryManager()
    knowledge_base = KnowledgeBase()
    db_manager = DBManager()
    workflow = SupportTicketWorkflow(
        memory_manager=memory_manager,
        knowledge_base=knowledge_base,
        db_manager=db_manager,
    )
    tools = build_support_tools(knowledge_base)

    return workflow, tools
