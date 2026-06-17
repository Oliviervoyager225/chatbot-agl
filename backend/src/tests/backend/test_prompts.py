"""Tests for backend.agent.prompts."""

from backend.agent.prompts import SYSTEM_PROMPT


def test_system_prompt_mentions_qdrant_first():
    assert "qdrant_search_tool" in SYSTEM_PROMPT
    qdrant_pos = SYSTEM_PROMPT.index("qdrant_search_tool")
    web_pos = SYSTEM_PROMPT.index("web_search_tool")
    assert qdrant_pos < web_pos


def test_system_prompt_requires_sources():
    assert "Sources:" in SYSTEM_PROMPT


def test_system_prompt_forbids_fabrication():
    assert "never" in SYSTEM_PROMPT.lower() or "never" in SYSTEM_PROMPT
    assert "fabricat" in SYSTEM_PROMPT.lower() or "invent" in SYSTEM_PROMPT.lower()


def test_system_prompt_requires_same_language():
    assert "same language" in SYSTEM_PROMPT.lower()
