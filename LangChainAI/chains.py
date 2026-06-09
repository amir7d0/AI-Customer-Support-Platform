from __future__ import annotations

import json
from typing import Any

from .llm import get_llm
from .db import DBManager
from .knowledge import KnowledgeBase
from .logging__ import log_ticket_event
from .memory_manager import TicketMemoryManager
from .schemas import DraftResponse, TaskItem, TicketAnalysisResult, TicketMetadata
from .tools import build_support_tools, create_internal_task, escalate_ticket

from .config import Settings

class TicketAnalyzer:
    """Analyzes support tickets using structured output with LLM.invoke."""
    
    def __init__(self) -> None:
        # Bind LLM with structured output for TicketAnalysisResult
        self.llm = get_llm().with_structured_output(TicketAnalysisResult)

    def analyze(self, ticket: TicketMetadata) -> TicketAnalysisResult:
        """Analyze ticket using direct LLM invocation."""
        prompt = (
            "You are an AI support analyst. Analyze the incoming customer ticket and produce a structured response. "
            "Provide a category, priority, escalation decision, escalation reason, a list of internal tasks, and knowledge queries for retrieval.\n\n"
            f"Ticket subject: {ticket.subject}\n"
            f"Ticket sender: {ticket.sender}\n"
            f"Ticket body:\n{ticket.body}\n\n"
            "Return a structured response matching the expected output format."
        )
        
        analysis = self.llm.invoke(prompt)

        # Ensure tasks are TaskItem objects with ticket_id
        tasks = []
        for task in analysis.tasks:
            if isinstance(task, TaskItem):
                tasks.append(task)
            else:
                tasks.append(TaskItem(**task, ticket_id=ticket.ticket_id))

        return TicketAnalysisResult(
            category=analysis.category,
            priority=analysis.priority,
            escalate=analysis.escalate,
            escalation_reason=analysis.escalation_reason,
            tasks=tasks,
            knowledge_queries=analysis.knowledge_queries,
        )


class ResponseComposer:
    """Composes support responses using LLM.invoke."""
    
    def __init__(self) -> None:
        self.llm = get_llm()

    def compose(
        self,
        ticket: TicketMetadata,
        analysis: TicketAnalysisResult,
        knowledge: dict[str, Any],
        previous_summaries: list[dict[str, str]] | None = None,
    ) -> DraftResponse:
        """Compose response using direct LLM invocation."""
        previous_context = "\n".join(
            [f"[{item['ticket_id']}] {item['summary']}" for item in (previous_summaries or [])]
        )
        knowledge_text = f"{knowledge['answer']}\nSources: {knowledge['sources']}"
        if previous_context:
            knowledge_text = f"{knowledge_text}\n\nRecent similar ticket summaries:\n{previous_context}"

        prompt = (
            "You are a customer support agent drafting a professional response. "
            "Use the ticket details, the analysis output, and the retrieved knowledge summary below. "
            "Be concise, empathetic, and include the next recommended step.\n\n"
            f"Ticket subject: {ticket.subject}\n"
            f"Ticket sender: {ticket.sender}\n"
            f"Ticket body:\n{ticket.body}\n\n"
            f"Analysis:\n{analysis.model_dump_json(indent=2)}\n\n"
            f"Retrieved knowledge:\n{knowledge_text}\n\n"
            "Draft the reply and include any follow-up suggestion for internal teams."
        )

        response_text = self.llm.invoke(prompt)

        return DraftResponse(
            response=response_text.content if hasattr(response_text, "content") else str(response_text),
            follow_up_instructions=(
                "Review any escalation recommendations and create follow-up tasks in the support system."
            ),
        )


class SupportTicketWorkflow:
    """Orchestrates the ticket processing workflow."""
    
    def __init__(
        self,
        memory_manager: TicketMemoryManager,
        knowledge_base: KnowledgeBase,
        db_manager: DBManager,
    ) -> None:
        self.memory_manager = memory_manager
        self.knowledge_base = knowledge_base
        self.db_manager = db_manager
        self.analyzer = TicketAnalyzer()
        self.composer = ResponseComposer()

    def process_ticket(self, ticket: TicketMetadata, commit: bool = True) -> dict[str, Any]:
        """Process ticket through analysis, knowledge retrieval, and response composition."""
        self.memory_manager.add_memory(ticket.body)
        analysis = self.analyzer.analyze(ticket)
        event_type = "ticket_analyzed" if commit else "ticket_preview"
        log_ticket_event(ticket.ticket_id, event_type, analysis.model_dump())

        persistent_matches = self.memory_manager.search_persistent_history(ticket.subject)
        knowledge = self.knowledge_base.query(" ".join(analysis.knowledge_queries))

        response = self.composer.compose(
            ticket=ticket,
            analysis=analysis,
            knowledge=knowledge,
            previous_summaries=persistent_matches,
        )

        escalation_note = None
        task_outputs: list[str] = []
        
        if commit:
            # Execute tools for internal actions
            for task in analysis.tasks:
                task_description = create_internal_task(
                    ticket_id=ticket.ticket_id,
                    title=task.title,
                    details=task.description,
                    priority=task.priority,
                )
                task_outputs.append(task_description)

            if analysis.escalate:
                escalation_note = escalate_ticket(ticket.ticket_id, analysis.escalation_reason)

            # Persist to database
            self.db_manager.save_ticket(ticket)
            self.db_manager.save_analysis(ticket.ticket_id, analysis)
            self.db_manager.save_response(ticket.ticket_id, response)
            for task in analysis.tasks:
                self.db_manager.save_task(ticket.ticket_id, task)

            log_ticket_event(
                ticket.ticket_id,
                "ticket_completed",
                {
                    "analysis": analysis.model_dump(),
                    "response": response.model_dump(),
                    "tasks": [task.model_dump() for task in analysis.tasks],
                    "escalation_note": escalation_note,
                },
            )

            self.memory_manager.add_ticket_summary(
                ticket.ticket_id,
                f"{ticket.subject} | category={analysis.category} | priority={analysis.priority} | escalate={analysis.escalate}",
            )
        else:
            log_ticket_event(
                ticket.ticket_id,
                "ticket_preview_generated",
                {
                    "analysis": analysis.model_dump(),
                    "response": response.model_dump(),
                },
            )

        return {
            "ticket_id": ticket.ticket_id,
            "analysis": analysis.model_dump(),
            "response": response.model_dump(),
            "knowledge": knowledge,
            "tasks": [task.model_dump() for task in analysis.tasks],
            "escalation_note": escalation_note,
            "preview_mode": not commit,
        }
