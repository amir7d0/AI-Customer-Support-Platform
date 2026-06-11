# Agents

The customer support LangGraph workflow is defined in `src/deep_agent/graph.py`.

## Conventions

- Keep graph nodes small and testable.
- Prefer async-native code wherever possible for tools, tests, and I/O.
- New tools should be low-dependency and safe to run on a remote server.
- Runtime files should stay under `src/deep_agent/data` or `src/deep_agent/chroma_db`.
- Avoid hard-coded secrets; use `.env.example` for required variable names.
