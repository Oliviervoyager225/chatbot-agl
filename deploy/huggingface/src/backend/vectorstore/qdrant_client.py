"""Qdrant connection and collection helpers."""

import logging

from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import Distance, VectorParams

from backend.config import Settings

logger = logging.getLogger(__name__)

def get_qdrant_client(settings: Settings) -> QdrantClient:
    """Return a QdrantClient connected to the configured instance."""
    return QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
    )


def ensure_collection(client: QdrantClient, settings: Settings) -> None:
    """Create the Qdrant collection if it does not already exist."""
    try:
        client.get_collection(settings.qdrant_collection)
        logger.info("Collection '%s' already exists", settings.qdrant_collection)
    except (UnexpectedResponse, ValueError):
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(
                size=settings.embedding_dim,
                distance=Distance.COSINE,
            ),
        )
        logger.info("Created collection '%s'", settings.qdrant_collection)
