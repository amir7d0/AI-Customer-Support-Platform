from __future__ import annotations

from typing import Any

from .llm import get_llm
from .schemas import DraftResponse, TaskItem, TicketAnalysisResult, TicketMetadata


class TicketAnalyzer:
    def __init__(self) -> None:
        self.llm = get_llm().with_structured_output(TicketAnalysisResult)

    def analyze(self, ticket: TicketMetadata) -> TicketAnalysisResult:
        prompt = (
            "You are an AI support analyst. Analyze the incoming customer ticket and produce a structured response. "
            "Provide a category, priority, escalation decision, escalation reason, a list of internal tasks, and knowledge queries for retrieval.\n\n"
            f"Ticket subject: {ticket.subject}\n"
            f"Ticket sender: {ticket.sender}\n"
            f"Ticket body:\n{ticket.body}\n\n"
            "Return a structured response matching the expected output format."
        )

        analysis = self.llm.invoke(prompt)
        tasks = [
            task if isinstance(task, TaskItem) else TaskItem(**task, ticket_id=ticket.ticket_id)
            for task in analysis.tasks
        ]

        return TicketAnalysisResult(
            category=analysis.category,
            priority=analysis.priority,
            escalate=analysis.escalate,
            escalation_reason=analysis.escalation_reason or ("Escalated by analysis." if analysis.escalate else ""),
            tasks=tasks,
            knowledge_queries=analysis.knowledge_queries,
        )


class ResponseComposer:
    def __init__(self) -> None:
        self.llm = get_llm()

    def compose(
        self,
        ticket: TicketMetadata,
        analysis: TicketAnalysisResult,
        knowledge: dict[str, Any],
        previous_summaries: list[dict[str, str]] | None = None,
    ) -> DraftResponse:
        previous_context = "\n".join(
            f"[{item['ticket_id']}] {item['summary']}"
            for item in (previous_summaries or [])
        )
        knowledge_text = f"{knowledge.get('answer', '')}\nSources: {knowledge.get('sources', [])}"
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
        response_content = response_text.content if hasattr(response_text, "content") else str(response_text)

        return DraftResponse(
            response=response_content,
            follow_up_instructions="Review any escalation recommendations and create follow-up tasks in the support system.",
        )
