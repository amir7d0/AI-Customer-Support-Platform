# AI Customer Support Platform - LangGraph

LangGraph implementation of the customer support email handler.

## What this project provides

- A deployable LangGraph workflow at `src/deep_agent/graph.py`.
- Ticket parsing, analysis, knowledge retrieval, response drafting, task creation, escalation, and persistence.
- Chroma or Qdrant vector storage for the knowledge base.
- SQLite ticket storage and JSON ticket memory under `src/deep_agent/data`.
- Unit tests for graph compilation.

## Prerequisites

- An API key for your model provider.
- A configured embedding provider.
- Chroma for local vector storage, or Qdrant for remote vector storage.

## Quickstart

1. Copy environment defaults:

```bash
cp .env.example .env
```

2. Set your provider credentials in `.env`.

3. Run the sample file:

```bash
python sample_run.py --commit
```


4. Start the local LangGraph dev server:

```bash
uv run langgraph dev
```

5. Run unit tests:

```bash
uv run python -m pytest tests/unit_tests -q
```

## Runtime paths

Runtime artifacts are resolved relative to `src/deep_agent`, not the project working directory:

- SQLite database: `src/deep_agent/data/support.db`
- Ticket memory: `src/deep_agent/data/ticket_archive.json`
- Chroma store: `src/deep_agent/chroma_db`
- Knowledge source: `src/deep_agent/docs/info.md`

