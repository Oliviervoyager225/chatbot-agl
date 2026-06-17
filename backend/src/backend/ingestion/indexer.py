"""Build / refresh the Qdrant collection from scraped page data."""

import logging
import uuid

from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from backend.config import Settings
from backend.ingestion.embedder import get_embeddings
from backend.ingestion.loader import load_pages
from backend.vectorstore.qdrant_client import ensure_collection, get_qdrant_client

logger = logging.getLogger(__name__)


def _deterministic_id(link: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, link))


def _get_existing_links(client: QdrantClient, collection: str) -> set[str]:
    """Scroll through all Qdrant points and return the set of indexed links."""
    existing: set[str] = set()
    offset = None
    while True:
        points, next_offset = client.scroll(
            collection_name=collection,
            limit=256,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )
        for point in points:
            link = (point.payload or {}).get("metadata", {}).get("link", "")
            if link:
                existing.add(link)
        if next_offset is None:
            break
        offset = next_offset
    return existing


def _upsert_pages(pages: list[dict], settings: Settings) -> int:
    """Embed and upsert the given pages into Qdrant. Returns count inserted."""
    if not pages:
        return 0

    client = get_qdrant_client(settings)
    ensure_collection(client, settings)
    embeddings = get_embeddings(settings)

    documents = [
        Document(
            page_content=page["text"],
            metadata={
                "title": page["title"],
                "link": page["link"],
                "source_file": page["source_file"],
            },
        )
        for page in pages
    ]
    ids = [_deterministic_id(page["link"]) for page in pages]

    store = QdrantVectorStore(
        client=client,
        collection_name=settings.qdrant_collection,
        embedding=embeddings,
    )
    store.add_documents(documents, ids=ids)

    logger.info(
        "Indexed %d documents into '%s'", len(documents), settings.qdrant_collection
    )
    return len(documents)


def sync_new_pages(settings: Settings) -> int:
    """Index only pages that are not already in Qdrant.

    Returns the number of newly indexed documents.
    """
    pages = load_pages(settings.scrape_data_dir)
    if not pages:
        logger.info("No pages on disk — nothing to sync")
        return 0

    client = get_qdrant_client(settings)
    ensure_collection(client, settings)
    existing_links = _get_existing_links(client, settings.qdrant_collection)

    new_pages = [p for p in pages if p["link"] not in existing_links]
    if not new_pages:
        logger.info("All %d pages already indexed — nothing new to sync", len(pages))
        return 0

    logger.info(
        "Found %d new pages out of %d total — indexing", len(new_pages), len(pages)
    )
    return _upsert_pages(new_pages, settings)


def index_pages(settings: Settings) -> int:
    """Load all pages, embed them, and upsert into Qdrant (full re-index).

    Returns the number of documents indexed.
    """
    pages = load_pages(settings.scrape_data_dir)
    if not pages:
        logger.warning("Nothing to index — no pages loaded")
        return 0
    return _upsert_pages(pages, settings)
