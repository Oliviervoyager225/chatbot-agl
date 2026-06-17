"""Tests for backend.config."""

from pathlib import Path

from backend.config import PROJECT_ROOT, Settings


def test_project_root_is_valid():
    assert (PROJECT_ROOT / "pyproject.toml").exists()


def test_settings_loads_from_env(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "g-key")
    settings = Settings()
    assert settings.google_api_key == "g-key"


def test_settings_defaults(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "g")
    settings = Settings()
    assert settings.qdrant_url == "http://localhost:6333"
    assert settings.qdrant_collection == "agl_website"
    assert settings.top_k == 5
    assert isinstance(settings.scrape_data_dir, Path)
