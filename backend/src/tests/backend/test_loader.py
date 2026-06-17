"""Tests for backend.ingestion.loader."""

import json

from backend.ingestion.loader import load_pages


def test_load_pages_reads_json(tmp_data_dir):
    pages = load_pages(tmp_data_dir)
    assert len(pages) == 2
    assert pages[0]["title"] == "Home"
    assert pages[1]["link"] == "https://www.aglgroup.com/services"
    assert all("source_file" in p for p in pages)


def test_load_pages_adds_source_file(tmp_data_dir):
    pages = load_pages(tmp_data_dir)
    assert pages[0]["source_file"] == "pages.json"


def test_load_pages_skips_empty_text(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "empty.json").write_text(
        json.dumps([{"title": "Empty", "text": "", "link": "http://x"}]),
        encoding="utf-8",
    )
    pages = load_pages(data_dir)
    assert len(pages) == 0


def test_load_pages_skips_whitespace_only_text(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "ws.json").write_text(
        json.dumps([{"title": "Blank", "text": "   \n  ", "link": "http://x"}]),
        encoding="utf-8",
    )
    pages = load_pages(data_dir)
    assert len(pages) == 0


def test_load_pages_empty_dir(tmp_path):
    data_dir = tmp_path / "empty"
    data_dir.mkdir()
    pages = load_pages(data_dir)
    assert pages == []


def test_load_pages_handles_malformed_json(tmp_path):
    data_dir = tmp_path / "bad"
    data_dir.mkdir()
    (data_dir / "bad.json").write_text("{not valid json", encoding="utf-8")
    pages = load_pages(data_dir)
    assert pages == []
