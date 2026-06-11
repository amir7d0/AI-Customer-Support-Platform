# AI Customer Support Platform

A customer support email handling platform with two orchestration engines:

- `LangChainAI`: LangChain-based ticket analysis, retrieval, response drafting, task creation, escalation, and persistence.
- `LangGraphAI`: LangGraph state-graph implementation of the same support workflow.

The Streamlit frontend can run either engine from one UI.

## Project layout

```text
.
├── frontend.py                 # Streamlit UI for LangChain and LangGraph
├── LangChainAI/                # LangChain implementation
├── LangGraphAI/                # LangGraph implementation
│   ├── src/deep_agent/         # LangGraph package
│   ├── langgraph.json          # LangGraph deployment config
│   ├── pyproject.toml          # LangGraph dependencies
│   └── sample_run.py           # CLI sample for the LangGraph workflow
└── README.md
```

## Runtime storage

Each engine keeps its runtime artifacts inside its own package directory.

### LangChainAI

- SQLite database: `LangChainAI/data/support.db`
- Ticket archive: `LangChainAI/data/ticket_archive.json`
- Chroma store: `LangChainAI/chroma_db`
- Event log: `LangChainAI/data/support_events.log`
- Knowledge source: `LangChainAI/docs/info.md`

### LangGraphAI

- SQLite database: `LangGraphAI/src/deep_agent/data/support.db`
- Ticket archive: `LangGraphAI/src/deep_agent/data/ticket_archive.json`
- Chroma store: `LangGraphAI/src/deep_agent/chroma_db`
- Knowledge source: `LangGraphAI/src/deep_agent/docs/info.md`

## Setup

This project uses `uv` for dependency management.

```bash
uv sync
```

The LangGraph project has its own dependency set. If you want to run LangGraph commands from inside that directory:

```bash
cd LangGraphAI
uv sync
```

## Environment configuration

Copy or create environment files from the examples where available. Do not commit real API keys.

Important variables include:

```bash
LLM_PROVIDER=nvidia
LLM_MODEL=nvidia/nemotron-3-nano-omni-30b-a3b-reasoning
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://integrate.api.nvidia.com/v1

EMBEDDING_PROVIDER=nvidia
EMBEDDING_MODEL=nvidia/llama-nemotron-embed-1b-v2
EMBEDDING_BASE_URL=https://integrate.api.nvidia.com/v1

VECTOR_STORE_PROVIDER=chroma
CHROMA_COLLECTION_NAME=ai_support_documents

DATABASE_DIR=data
ENABLE_TRACING=false
USE_HUMAN_REVIEW_CALLBACK=false
```

Use `qdrant` for `VECTOR_STORE_PROVIDER` if you want remote Qdrant storage instead of local Chroma.

## Run the Streamlit frontend

Start the shared UI from the project root:

```bash
uv run streamlit run frontend.py
```

The sidebar includes an `Orchestration Engine` selector:

- `LangChain` uses `LangChainAI.service.create_support_service()`.
- `LangGraph` uses `LangGraphAI/src/deep_agent/nodes.SupportTicketWorkflow`.

Recent tickets are loaded from the selected engine's own SQLite database.

## Run LangChainAI

Run the LangChain sample workflow:

```bash
uv run python -m LangChainAI.sample_run
```

Or run it as a script:

```bash
uv run python LangChainAI/sample_run.py
```

## Run LangGraphAI

Run the LangGraph sample workflow from the project root:

```bash
uv run python LangGraphAI/sample_run.py
```

Run with persistence and internal action creation:

```bash
uv run python LangGraphAI/sample_run.py --commit
```

Start the LangGraph dev server from the LangGraph project directory:

```bash
cd LangGraphAI
uv run langgraph dev
```

If you run `langgraph dev` from the project root, point it at the LangGraph config:

```bash
uv run langgraph dev --config LangGraphAI/langgraph.json
```

## Tests and checks

Root project syntax check:

```bash
uv run python -m compileall -q frontend.py LangChainAI
```

LangGraphAI unit tests:

```bash
cd LangGraphAI
uv run python -m pytest tests/unit_tests -q
```

LangGraphAI lint:

```bash
cd LangGraphAI
uv run python -m ruff check src tests
```

## Notes

- The frontend applies runtime settings to environment variables before creating a workflow.
- LangGraph runtime paths are resolved relative to `LangGraphAI/src/deep_agent`, so running from the root or from another directory does not create `data` or `chroma_db` in the project root.
- Generated responses should be reviewed before sending to customers.
