# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RAG-first enterprise chatbot for Africa Global Logistics (AGL). Answers user questions by searching a Qdrant knowledge base (scraped from aglgroup.com), falling back to DuckDuckGo web search when the knowledge base has no relevant results.

## Tech Stack

- Python 3.12, managed with **uv**
- **LangGraph** + **LangChain** for agent orchestration
- **Gemini** (`gemini-3-flash-preview`) for LLM, `gemini-embedding-001` for embeddings
- **Qdrant** for vector storage (3072-dim cosine)
- **DuckDuckGo** for web search fallback
- **FastAPI** + **uvicorn** for API deployment (SSE streaming)
- **Gradio** for web UI
- **pydantic-settings** for configuration
- **BeautifulSoup4** for web scraping

## Commands

```bash
# Docker Compose (recommended)
docker compose up --build              # Start Qdrant + backend
docker compose up -d                   # Start in background
docker compose down                    # Stop all services

# Local development (run python -m commands from src/)
uv sync --extra dev                       # Install all deps
python -m backend.scripts.ingest          # Full re-index into Qdrant
python -m backend.gradio                  # Start Gradio web UI (localhost:7860)
python -m backend.main                    # Terminal chatbot (interactive, streaming)
uvicorn backend.app.api:app --host 0.0.0.0 --port 8000  # FastAPI server
python src/backend/utils/crawler.py       # Full website crawl
python src/backend/utils/crawler.py --single <URL>  # Single page extract
pytest -v                                 # Run all tests
pytest src/tests/backend/test_loader.py::test_load_pages_reads_json  # Single test
ruff check src/                           # Lint
black --target-version py312 src/         # Format
```

## Architecture

- `src/backend/config.py` — `Settings` via pydantic-settings, loads `.env` from project root (`PROJECT_ROOT = Path(__file__).resolve().parents[2]`)
- `src/backend/ingestion/` — Data pipeline: `loader.py` reads JSON, `embedder.py` wraps Gemini embeddings, `indexer.py` upserts into Qdrant (1 page = 1 chunk, deterministic UUIDs via `uuid5` of link). `sync_new_pages()` indexes only new documents (skips already-indexed links).
- `src/backend/vectorstore/qdrant_client.py` — Qdrant connection + auto-creates collection (3072-dim cosine)
- `src/backend/tools/` — LangChain `@tool` functions: `qdrant_search.py` (RAG) and `web_search.py` (DuckDuckGo fallback)
- `src/backend/agent/` — LangGraph `StateGraph`: `state.py` (AgentState), `prompts.py` (system prompt with scope/style/rules), `llm.py` (Gemini factory), `graph.py` (agent→tools→agent loop with `ToolNode` + `tools_condition`)
- `src/backend/gradio.py` — Gradio web UI entrypoint (streaming)
- `src/backend/main.py` — Terminal chatbot entrypoint (streaming)
- `src/backend/app/` — FastAPI deployment: `api.py` (health, chat SSE, ingest endpoints), `schemas.py` (Pydantic models)
- `src/backend/utils/crawler.py` — BFS web crawler for aglgroup.com, supports `--single` for one page
- `data/website_scrape/` — Scraped JSON data (each file is `[{title, text, link}]`)
- `src/tests/backend/` — Pytest suite with all external deps mocked

## Key Design Decisions

- The agent MUST call `qdrant_search_tool` first; `web_search_tool` is only a fallback.
- The agent only answers AGL-related questions; off-topic queries are politely declined.
- System prompt enforces: cite only `link`/`url`, deduplicate sources, reply in user's language, be concise, never fabricate.
- All three entrypoints (Gradio, CLI, FastAPI) stream responses token-by-token and sync new documents on startup via `sync_new_pages()`.
- Gemini returns `content` as a list of parts (not a plain string) — streaming filters must handle both `str` and `list` content formats.
- Package is `backend` (importable from `src/backend/`), configured via `[tool.setuptools.packages.find] where = ["src"]`.
- Tests use `pythonpath = ["src"]` in pyproject.toml so `backend` is importable without install.
