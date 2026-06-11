from __future__ import annotations

import os
from typing import Any

import streamlit as st
from LangChainAI.schemas import TicketMetadata
# from LangChain.service import create_support_service
from LangChainAI.db import DBManager
from LangChainAI.config import settings
from LangChainAI.service import create_support_service

def apply_runtime_settings(config: dict[str, Any]) -> None:
    for key, value in config.items():
        if value is None:
            continue
        os.environ[key] = str(value)


def render_config_sidebar() -> dict[str, Any]:
    st.sidebar.title("System Configuration")
    engine = st.sidebar.selectbox("Orchestration Engine", ["LangChain", "LangGraph"])
    st.sidebar.markdown("---")

    base_url = st.sidebar.text_input("LLM API Base URL", value=os.environ.get("LLM_BASE_URL", ""))
    llm_model = st.sidebar.text_input("LLM Model", value=os.environ.get("LLM_MODEL", ""))
    temperature = st.sidebar.slider("Temperature", 0.0, 1.0, float(os.environ.get("LLM_TEMPERATURE")), 0.05)
    streaming = st.sidebar.checkbox("Enable streaming", value=os.environ.get("STREAMING") == "True")
    use_review = st.sidebar.checkbox("Require human approval", value=False)

    st.sidebar.markdown("---")
    if settings.VECTOR_STORE_PROVIDER == "chroma":
        chroma_url = st.sidebar.text_input("Chroma URL", value=os.environ.get("CHROMA_URL", "http://localhost:8000"))
    elif settings.VECTOR_STORE_PROVIDER == "qdrant":
        qdrant_url = st.sidebar.text_input("Qdrant URL", value=os.environ.get("QDRANT_URL", "http://localhost:6333"))
        qdrant_api_key = st.sidebar.text_input("Qdrant API Key", value=os.environ.get("QDRANT_API_KEY", ""))
        qdrant_collection = st.sidebar.text_input("Qdrant Collection", value=os.environ.get("QDRANT_COLLECTION_NAME", "ai_support_documents"))

    return {
        "engine": engine,
        "LLM_BASE_URL": base_url,
        "LLM_MODEL": llm_model,
        "LLM_TEMPERATURE": temperature,
        "STREAMING": streaming,
        "USE_HUMAN_REVIEW_CALLBACK": use_review,
        "CHROMA_URL": chroma_url if settings.VECTOR_STORE_PROVIDER == "chroma" else None,
        "QDRANT_URL": qdrant_url if settings.VECTOR_STORE_PROVIDER == "qdrant" else None,
    }


def run_app() -> None:
    st.set_page_config(page_title="AI Customer Support Platform", layout="wide")
    st.title("AI Customer Support Platform")
    st.write("Use this interface to submit support tickets and review AI-generated drafts.")
    
    apply_runtime_settings(settings.model_dump())
    config = render_config_sidebar()

    if config["engine"] == "LangGraph":
        st.warning("LangGraph support is not implemented yet. Select LangChain to continue.")

    st.subheader("New ticket")
    sender = st.text_input("Sender email", value="customer@example.com")
    subject = st.text_input("Subject", value="Issue with my account")
    body = st.text_area("Body", value="I cannot access my dashboard after resetting my password.")

    if "preview_data" not in st.session_state:
        st.session_state.preview_data = None
    if "ticket_payload" not in st.session_state:
        st.session_state.ticket_payload = None

    preview_button = st.button("Generate draft")
    db_manager = DBManager()

    if preview_button:
        if config["engine"] != "LangChain":
            st.error("Only LangChain is available currently.")
        else:
            workflow, tools = create_support_service()
            ticket = TicketMetadata(sender=sender, subject=subject, body=body)
            preview = workflow.process_ticket(ticket, commit=False)
            
            st.session_state.preview_data = preview
            st.session_state.ticket_payload = ticket

    if st.session_state.preview_data is not None:
        st.subheader("Draft analysis and response")
        st.json(st.session_state.preview_data)
        if config["USE_HUMAN_REVIEW_CALLBACK"]:
            st.info("Human review is enabled. Approve the ticket to persist it and create tasks.")

        if st.button("Approve and submit ticket"):
            workflow, tools = create_support_service()
            ticket = st.session_state.ticket_payload
            persisted = workflow.process_ticket(ticket, commit=True)
            
            st.success("Ticket has been submitted and stored in SQLite.")
            st.subheader("Final ticket result")
            st.json(persisted)
            st.session_state.preview_data = None
            st.session_state.ticket_payload = None

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
