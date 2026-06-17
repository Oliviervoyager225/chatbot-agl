"""CLI script to ingest scraped data into Qdrant.

Usage:
    python -m backend.scripts.ingest
"""

from backend.config import Settings
from backend.ingestion.indexer import index_pages
from backend.logging_config import setup_logging


def main() -> None:
    """Run the ingestion pipeline."""
    setup_logging()
    settings = Settings()
    count = index_pages(settings)
    print(f"Ingestion complete — {count} documents indexed.")


if __name__ == "__main__":
    main()
