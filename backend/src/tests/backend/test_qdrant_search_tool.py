"""Tests for backend.tools.qdrant_search."""

from unittest.mock import MagicMock, patch

from langchain_core.documents import Document


@patch("backend.tools.qdrant_search.Settings")
@patch("backend.tools.qdrant_search._get_store")
def test_qdrant_search_returns_results(mock_get_store, mock_settings_cls):
    mock_settings_cls.return_value = MagicMock(top_k=2)

    mock_store = MagicMock()
    mock_store.similarity_search_with_score.return_value = [
        (
            Document(
                page_content="AGL logistics content",
                metadata={"title": "Home", "link": "https://aglgroup.com/"},
            ),
            0.95,
        ),
    ]
    mock_get_store.return_value = mock_store

    from backend.tools.qdrant_search import qdrant_search_tool

    results = qdrant_search_tool.invoke("AGL logistics")

    assert len(results) == 1
    assert results[0]["title"] == "Home"
    assert results[0]["link"] == "https://aglgroup.com/"
    assert results[0]["score"] == 0.95
    assert "AGL logistics content" in results[0]["text"]


@patch("backend.tools.qdrant_search.Settings")
@patch("backend.tools.qdrant_search._get_store")
def test_qdrant_search_empty(mock_get_store, mock_settings_cls):
    mock_settings_cls.return_value = MagicMock(top_k=5)
    mock_store = MagicMock()
    mock_store.similarity_search_with_score.return_value = []
    mock_get_store.return_value = mock_store

    from backend.tools.qdrant_search import qdrant_search_tool

    results = qdrant_search_tool.invoke("nonexistent topic")
    assert results == []
