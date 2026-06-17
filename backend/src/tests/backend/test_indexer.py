"""Tests for backend.ingestion.indexer."""

from unittest.mock import MagicMock, patch

from backend.ingestion.indexer import _deterministic_id, index_pages


def test_deterministic_id_is_stable():
    url = "https://www.aglgroup.com/"
    assert _deterministic_id(url) == _deterministic_id(url)


def test_deterministic_id_differs_for_different_urls():
    assert _deterministic_id("http://a") != _deterministic_id("http://b")


@patch("backend.ingestion.indexer.QdrantVectorStore")
@patch("backend.ingestion.indexer.get_embeddings")
@patch("backend.ingestion.indexer.get_qdrant_client")
@patch("backend.ingestion.indexer.ensure_collection")
def test_index_pages_creates_documents(
    mock_ensure, mock_client, mock_embed, mock_store_cls, mock_settings
):
    mock_store = MagicMock()
    mock_store_cls.return_value = mock_store

    count = index_pages(mock_settings)

    assert count == 2
    mock_store.add_documents.assert_called_once()
    docs, kwargs = mock_store.add_documents.call_args
    documents = docs[0]
    assert len(documents) == 2
    assert documents[0].metadata["title"] == "Home"
    assert documents[1].metadata["link"] == "https://www.aglgroup.com/services"
    assert len(kwargs["ids"]) == 2


@patch("backend.ingestion.indexer.load_pages", return_value=[])
def test_index_pages_no_data(mock_load, mock_settings):
    count = index_pages(mock_settings)
    assert count == 0
