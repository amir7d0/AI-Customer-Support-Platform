"""Customer support graph for LangGraph deployment."""

from __future__ import annotations

import contextlib

from langchain_core.runnables import RunnableConfig
from langgraph_sdk.runtime import ServerRuntime

from deep_agent.nodes import SupportTicketWorkflow

workflow = SupportTicketWorkflow()
graph = workflow.graph


@contextlib.asynccontextmanager
async def get_agent(config: RunnableConfig, runtime: ServerRuntime):
    del config, runtime
    yield graph
