from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

import streamlit as st
from LangChainAI.config import settings as langchain_settings
from LangChainAI.db import DBManager as LangChainDBManager
from LangChainAI.schemas import TicketMetadata as LangChainTicketMetadata
from LangChainAI.service import create_support_service

# LANGGRAPH_SRC = Path(__file__).resolve().parent / "LangGraphAI" / "src"
# if str(LANGGRAPH_SRC) not in sys.path:
#     sys.path.insert(0, str(LANGGRAPH_SRC))

from LangGraphAI.src.deep_agent.config import settings as langgraph_settings
from LangGraphAI.src.deep_agent.db import DBManager as LangGraphDBManager  
from LangGraphAI.src.deep_agent.nodes import SupportTicketWorkflow as LangGraphSupportTicketWorkflow 
from LangGraphAI.src.deep_agent.schemas import TicketMetadata as LangGraphTicketMetadata 


def apply_runtime_settings(config: dict[str, Any]) -> None:
    for key, value in config.items():
        if value is None:
            continue
        os.environ[key] = str(value)


def render_config_sidebar() -> dict[str, Any]:
    st.sidebar.title("System Configuration")
    engine = st.sidebar.selectbox("Orchestration Engine", ["LangChain", "LangGraph"])
    active_settings = langgraph_settings if engine == "LangGraph" else langchain_settings
    st.sidebar.markdown("---")

    base_url = st.sidebar.text_input("LLM API Base URL", value=os.environ.get("LLM_BASE_URL", ""))
    llm_model = st.sidebar.text_input("LLM Model", value=os.environ.get("LLM_MODEL", ""))
    temperature = st.sidebar.slider(
        "Temperature",
        0.0,
        1.0,
        float(os.environ.get("LLM_TEMPERATURE", active_settings.LLM_TEMPERATURE)),
        0.05,
    )
    streaming = st.sidebar.checkbox("Enable streaming", value=os.environ.get("STREAMING") == "True")
    use_review = st.sidebar.checkbox("Require human approval", value=False)

    st.sidebar.markdown("---")
    chroma_url = None
    qdrant_url = None
    qdrant_api_key = None
    qdrant_collection = None

    if active_settings.VECTOR_STORE_PROVIDER == "chroma":
        chroma_url = st.sidebar.text_input("Chroma URL", value=os.environ.get("CHROMA_URL", "http://localhost:8000"))
    elif active_settings.VECTOR_STORE_PROVIDER == "qdrant":
        qdrant_url = st.sidebar.text_input("Qdrant URL", value=os.environ.get("QDRANT_URL", "http://localhost:6333"))
        qdrant_api_key = st.sidebar.text_input("Qdrant API Key", value=os.environ.get("QDRANT_API_KEY", ""))
        qdrant_collection = st.sidebar.text_input(
            "Qdrant Collection",
            value=os.environ.get("QDRANT_COLLECTION_NAME", "ai_support_documents"),
        )

    return {
        "engine": engine,
        "LLM_BASE_URL": base_url,
        "LLM_MODEL": llm_model,
        "LLM_TEMPERATURE": temperature,
        "STREAMING": streaming,
        "USE_HUMAN_REVIEW_CALLBACK": use_review,
        "CHROMA_URL": chroma_url,
        "QDRANT_URL": qdrant_url,
        "QDRANT_API_KEY": qdrant_api_key,
        "QDRANT_COLLECTION_NAME": qdrant_collection,
    }


def get_ticket_model(engine: str):
    return LangGraphTicketMetadata if engine == "LangGraph" else LangChainTicketMetadata


def create_workflow(engine: str):
    if engine == "LangGraph":
        return LangGraphSupportTicketWorkflow()
    workflow, _ = create_support_service()
    return workflow


def get_db_manager(engine: str):
    return LangGraphDBManager() if engine == "LangGraph" else LangChainDBManager()


def run_app() -> None:
    st.set_page_config(page_title="AI Customer Support Platform", layout="wide")
    st.title("AI Customer Support Platform")
    st.write("Use this interface to submit support tickets and review AI-generated drafts.")

    apply_runtime_settings(langchain_settings.model_dump())
    config = render_config_sidebar()

    st.subheader("New ticket")
    sender = st.text_input("Sender email", value="customer@example.com")
    subject = st.text_input("Subject", value="Issue with my account")
    body = st.text_area("Body", value="I cannot access my dashboard after resetting my password.")

    if "preview_data" not in st.session_state:
        st.session_state.preview_data = None
    if "ticket_payload" not in st.session_state:
        st.session_state.ticket_payload = None
    if "preview_engine" not in st.session_state:
        st.session_state.preview_engine = None

    preview_button = st.button("Generate draft")
    db_manager = get_db_manager(config["engine"])

    if preview_button:
        ticket_model = get_ticket_model(config["engine"])
        workflow = create_workflow(config["engine"])
        ticket = ticket_model(sender=sender, subject=subject, body=body)
        preview = workflow.process_ticket(ticket, commit=False)

        st.session_state.preview_data = preview
        st.session_state.ticket_payload = ticket
        st.session_state.preview_engine = config["engine"]

    if st.session_state.preview_data is not None:
        st.subheader("Draft analysis and response")
        st.json(st.session_state.preview_data)
        if config["USE_HUMAN_REVIEW_CALLBACK"]:
            st.info("Human review is enabled. Approve the ticket to persist it and create tasks.")

        if st.button("Approve and submit ticket"):
            workflow = create_workflow(st.session_state.preview_engine)
            ticket = st.session_state.ticket_payload
            persisted = workflow.process_ticket(ticket, commit=True)

            st.success("Ticket has been submitted and stored in SQLite.")
            st.subheader("Final ticket result")
            st.json(persisted)
            st.session_state.preview_data = None
            st.session_state.ticket_payload = None
            st.session_state.preview_engine = None

    st.sidebar.markdown("---")
    st.sidebar.subheader("Recent tickets")
    recent_tickets = db_manager.find_recent_tickets()
    if recent_tickets:
        for ticket in recent_tickets:
            st.sidebar.write(f"**{ticket['ticket_id']}** - {ticket['subject']} ({ticket['sender']})")
            st.sidebar.write(f"Received: {ticket['received_at']}  |  Stored: {ticket['created_at']}")
    else:
        st.sidebar.write("No tickets stored yet.")


if __name__ == "__main__":
    run_app()
