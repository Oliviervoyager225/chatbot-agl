"""Shared test fixtures."""

import json
from unittest.mock import MagicMock

import pytest

from backend.config import Settings

SAMPLE_PAGES = [
    {
        "title": "Home",
        "text": "Bienvenue chez AGL, opérateur logistique en Afrique.",
        "link": "https://www.aglgroup.com/",
    },
    {
        "title": "Services",
        "text": "AGL offre des services de transport et logistique.",
        "link": "https://www.aglgroup.com/services",
    },
]


@pytest.fixture()
def sample_pages():
    return SAMPLE_PAGES.copy()


@pytest.fixture()
def tmp_data_dir(tmp_path):
    """Create a temporary data directory with a sample JSON file."""
    data_dir = tmp_path / "website_scrape"
    data_dir.mkdir()
    (data_dir / "pages.json").write_text(json.dumps(SAMPLE_PAGES), encoding="utf-8")
    return data_dir


@pytest.fixture()
def mock_settings(tmp_data_dir):
    """Return a Settings instance with test values."""
    return Settings(
        google_api_key="test-google-key",
        qdrant_url="http://localhost:6333",
        qdrant_collection="test_collection",
        scrape_data_dir=tmp_data_dir,
    )


@pytest.fixture()
def mock_embeddings():
    """Return a mock embeddings object."""
    mock = MagicMock()
    mock.embed_documents.return_value = [[0.1] * 768, [0.2] * 768]
    mock.embed_query.return_value = [0.1] * 768
    return mock
