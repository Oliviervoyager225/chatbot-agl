"""Pydantic models for the FastAPI endpoints."""

from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str
    thread_id: str | None = None


class IngestResponse(BaseModel):
    indexed: int


class HealthResponse(BaseModel):
    status: str = "ok"
