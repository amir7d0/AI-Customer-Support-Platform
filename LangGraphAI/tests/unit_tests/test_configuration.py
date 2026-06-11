from langgraph.pregel import Pregel

from deep_agent.graph import graph
from deep_agent.nodes import SupportTicketWorkflow


def test_graph_compiles() -> None:
    assert isinstance(graph, Pregel)


def test_workflow_graph_compiles() -> None:
    workflow = SupportTicketWorkflow()
    assert isinstance(workflow.graph, Pregel)


def test_graph_nodes_are_configured() -> None:
    nodes = set(graph.nodes.keys())
    assert {
        "add_memory",
        "analyze_ticket",
        "retrieve_knowledge",
        "compose_response",
        "execute_actions",
    }.issubset(nodes)
