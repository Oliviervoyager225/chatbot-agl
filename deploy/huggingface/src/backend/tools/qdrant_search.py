"""Qdrant semantic search tool for the LangGraph agent."""

import logging

from langchain_core.tools import tool
from langchain_qdrant import QdrantVectorStore

from backend.config import Settings
from backend.ingestion.embedder import get_embeddings
from backend.vectorstore.qdrant_client import get_qdrant_client

logger = logging.getLogger(__name__)

_store: QdrantVectorStore | None = None


def _get_store() -> QdrantVectorStore:
    global _store
    if _store is None:
        settings = Settings()
        client = get_qdrant_client(settings)
        embeddings = get_embeddings(settings)
        _store = QdrantVectorStore(
            client=client,
            collection_name=settings.qdrant_collection,
            embedding=embeddings,
        )
    return _store


@tool
def qdrant_search_tool(query: str) -> list[dict]:
    """Search the AGL knowledge base for relevant information.

    Use this tool FIRST for any question about AGL, its services,
    logistics, or Africa Global Logistics.
    """
    settings = Settings()
    store = _get_store()
    results = store.similarity_search_with_score(query, k=settings.top_k)

    output = []
    for doc, score in results:
        output.append(
            {
                "title": doc.metadata.get("title", ""),
                "link": doc.metadata.get("link", ""),
                "text": doc.page_content,
                "score": round(score, 4),
            }
        )

    logger.info("Qdrant search for '%s' returned %d results", query, len(output))
    return output
