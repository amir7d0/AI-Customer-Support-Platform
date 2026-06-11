import os

import pytest
from langgraph.pregel import Pregel

from deep_agent.graph import graph
from deep_agent.nodes import SupportTicketWorkflow
from deep_agent.schemas import TicketMetadata


pytestmark = pytest.mark.anyio


def test_graph_compiles() -> None:
    assert isinstance(graph, Pregel)


def test_workflow_graph_compiles() -> None:
    workflow = SupportTicketWorkflow()
    assert isinstance(workflow.graph, Pregel)


async def test_support_ticket_preview() -> None:
    if not os.getenv("LLM_API_KEY"):
        pytest.skip("Set LLM_API_KEY to run preview integration.")

    workflow = SupportTicketWorkflow()
    result = workflow.process_ticket(
        TicketMetadata(
            sender="customer@example.com",
            subject="Cannot access my dashboard",
            body="I reset my password but still cannot log in.",
        ),
        commit=False,
    )

    assert result["analysis"]
    assert result["response"]
    assert result["preview_mode"] is True
