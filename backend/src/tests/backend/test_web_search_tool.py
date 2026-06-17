"""Tests for backend.tools.web_search."""

from unittest.mock import MagicMock, patch


@patch("backend.tools.web_search.DuckDuckGoSearchResults")
def test_web_search_returns_results(mock_ddg_cls):
    mock_ddg = MagicMock()
    mock_ddg.invoke.return_value = [
        {"title": "Result 1", "link": "https://example.com", "snippet": "Some info"},
    ]
    mock_ddg_cls.return_value = mock_ddg

    from backend.tools.web_search import web_search_tool

    results = web_search_tool.invoke("AGL shipping")

    assert len(results) == 1
    assert results[0]["title"] == "Result 1"
    assert results[0]["url"] == "https://example.com"
    assert results[0]["content"] == "Some info"


@patch("backend.tools.web_search.DuckDuckGoSearchResults")
def test_web_search_handles_string_result(mock_ddg_cls):
    mock_ddg = MagicMock()
    mock_ddg.invoke.return_value = "Plain text result"
    mock_ddg_cls.return_value = mock_ddg

    from backend.tools.web_search import web_search_tool

    results = web_search_tool.invoke("query")
    assert len(results) == 1
    assert results[0]["content"] == "Plain text result"
