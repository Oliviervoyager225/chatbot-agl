"""FastAPI application exposing the AGL chatbot agent."""

import logging
import uuid
from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessage, HumanMessage

from backend.agent.graph import get_compiled_graph
from backend.app.schemas import ChatRequest, HealthResponse, IngestResponse
from backend.config import Settings
from backend.ingestion.indexer import sync_new_pages
from backend.logging_config import setup_logging

logger = logging.getLogger(__name__)


def _extract_text(content: str | list) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            part.get("text", "") if isinstance(part, dict) else str(part)
            for part in content
        )
    return ""


def _stream_tokens(graph, question: str, thread_id: str) -> Iterator[str]:
    config = {"configurable": {"thread_id": thread_id}}
    for chunk, metadata in graph.stream(
        {"messages": [HumanMessage(content=question)]},
        config=config,
        stream_mode="messages",
    ):
        if metadata["langgraph_node"] != "agent":
            continue
        if not isinstance(chunk, AIMessage):
            continue
        text = _extract_text(chunk.content)
        if text:
            yield text


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    setup_logging()
    try:
        count = sync_new_pages(Settings())
        if count:
            logger.info("Startup sync: indexed %d new documents", count)
    except Exception:
        logger.exception("Startup sync failed — continuing without indexing")

    app.state.graph = get_compiled_graph()
    yield


app = FastAPI(title="AGL Chatbot API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse()


@app.post("/chat")
async def chat(body: ChatRequest) -> StreamingResponse:
    thread_id = body.thread_id or str(uuid.uuid4())
    graph = app.state.graph

    def event_stream() -> Iterator[str]:
        for token in _stream_tokens(graph, body.question, thread_id):
            yield f"data: {token}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/ingest", response_model=IngestResponse)
async def ingest() -> IngestResponse:
    count = sync_new_pages(Settings())
    return IngestResponse(indexed=count)
