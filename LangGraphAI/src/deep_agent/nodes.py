from __future__ import annotations

from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from .chains import ResponseComposer, TicketAnalyzer
from .db import DBManager
from .knowledge import KnowledgeBase
from .memory_manager import TicketMemoryManager
from .schemas import DraftResponse, TaskItem, TicketAnalysisResult, TicketMetadata
from .tools import create_internal_task, escalate_ticket


class TicketState(TypedDict):
    ticket: dict[str, Any]
    commit: bool
    analysis: dict[str, Any] | None
    knowledge: dict[str, Any] | None
    response: dict[str, Any] | None
    tasks: list[dict[str, Any]]
    task_outputs: list[str]
    escalation_note: str | None
    preview_mode: bool
    errors: list[str]


class SupportTicketGraphBuilder:
    def __init__(
        self,
        workflow: "SupportTicketWorkflow",
    ) -> None:
        self.workflow = workflow

    def build(self):
        graph = StateGraph(TicketState)
        graph.add_node("add_memory", self.add_memory)
        graph.add_node("analyze_ticket", self.analyze_ticket)
        graph.add_node("retrieve_knowledge", self.retrieve_knowledge)
        graph.add_node("compose_response", self.compose_response)
        graph.add_node("execute_actions", self.execute_actions)

        graph.add_edge(START, "add_memory")
        graph.add_edge("add_memory", "analyze_ticket")
        graph.add_edge("analyze_ticket", "retrieve_knowledge")
        graph.add_edge("retrieve_knowledge", "compose_response")
        graph.add_edge("compose_response", "execute_actions")
        graph.add_edge("execute_actions", END)

        return graph.compile()

    def add_memory(self, state: TicketState) -> dict[str, Any]:
        ticket = TicketMetadata.model_validate(state["ticket"])
        self.workflow.memory_manager.add_memory(ticket.body)
        return {}

    def analyze_ticket(self, state: TicketState) -> dict[str, Any]:
        ticket = TicketMetadata.model_validate(state["ticket"])
        analysis = self.workflow.analyzer.analyze(ticket)
        return {
            "analysis": analysis.model_dump(mode="json"),
            "tasks": [task.model_dump(mode="json") for task in analysis.tasks],
        }

    def retrieve_knowledge(self, state: TicketState) -> dict[str, Any]:
        analysis = TicketAnalysisResult.model_validate(state["analysis"])
        query = " ".join(analysis.knowledge_queries) or f"{ticket.subject or ''} {ticket.body}"
        knowledge = self.workflow.knowledge_base.query(query)
        return {"knowledge": knowledge}

    def compose_response(self, state: TicketState) -> dict[str, Any]:
        ticket = TicketMetadata.model_validate(state["ticket"])
        analysis = TicketAnalysisResult.model_validate(state["analysis"])
        knowledge = state.get("knowledge") or {}
        previous_summaries = self.workflow.memory_manager.search_persistent_history(ticket.subject or "")
        response = self.workflow.composer.compose(
            ticket=ticket,
            analysis=analysis,
            knowledge=knowledge,
            previous_summaries=previous_summaries,
        )
        return {"response": response.model_dump(mode="json")}

    def execute_actions(self, state: TicketState) -> dict[str, Any]:
        if not state.get("commit"):
            return {"preview_mode": True}

        ticket = TicketMetadata.model_validate(state["ticket"])
        analysis = TicketAnalysisResult.model_validate(state["analysis"])
        response = DraftResponse.model_validate(state["response"])

        task_outputs: list[str] = []
        for task_dict in state.get("tasks", []):
            task = TaskItem.model_validate(task_dict)
            task_outputs.append(
                create_internal_task(
                    ticket_id=ticket.ticket_id,
                    title=task.title,
                    details=task.description,
                    priority=task.priority,
                )
            )

        escalation_note = None
        if analysis.escalate:
            escalation_note = escalate_ticket(ticket.ticket_id, analysis.escalation_reason)

        self.workflow.db_manager.save_ticket(ticket)
        self.workflow.db_manager.save_analysis(ticket.ticket_id, analysis)
        self.workflow.db_manager.save_response(ticket.ticket_id, response)
        for task_dict in state.get("tasks", []):
            task = TaskItem.model_validate(task_dict)
            self.workflow.db_manager.save_task(ticket.ticket_id, task)

        self.workflow.memory_manager.add_ticket_summary(
            ticket.ticket_id,
            f"{ticket.subject} | category={analysis.category} | priority={analysis.priority} | escalate={analysis.escalate}",
        )

        return {
            "task_outputs": task_outputs,
            "escalation_note": escalation_note,
        }


class SupportTicketWorkflow:
    def __init__(
        self,
        memory_manager: TicketMemoryManager | None = None,
        knowledge_base: KnowledgeBase | None = None,
        db_manager: DBManager | None = None,
    ) -> None:
        self._memory_manager = memory_manager
        self._knowledge_base = knowledge_base
        self._db_manager = db_manager
        self._analyzer: TicketAnalyzer | None = None
        self._composer: ResponseComposer | None = None
        self.graph = SupportTicketGraphBuilder(self).build()

    @property
    def memory_manager(self) -> TicketMemoryManager:
        if self._memory_manager is None:
            self._memory_manager = TicketMemoryManager()
        return self._memory_manager

    @property
    def knowledge_base(self) -> KnowledgeBase:
        if self._knowledge_base is None:
            self._knowledge_base = KnowledgeBase()
        return self._knowledge_base

    @property
    def db_manager(self) -> DBManager:
        if self._db_manager is None:
            self._db_manager = DBManager()
        return self._db_manager

    @property
    def analyzer(self) -> TicketAnalyzer:
        if self._analyzer is None:
            self._analyzer = TicketAnalyzer()
        return self._analyzer

    @property
    def composer(self) -> ResponseComposer:
        if self._composer is None:
            self._composer = ResponseComposer()
        return self._composer

    def process_ticket(self, ticket: TicketMetadata, commit: bool = True) -> dict[str, Any]:
        state: TicketState = {
            "ticket": ticket.model_dump(mode="json"),
            "commit": commit,
            "analysis": None,
            "knowledge": None,
            "response": None,
            "tasks": [],
            "task_outputs": [],
            "escalation_note": None,
            "preview_mode": not commit,
            "errors": [],
        }
        return self.graph.invoke(state)
