"""Application settings loaded from environment variables / .env file."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Central configuration for the AGL chatbot backend."""

    google_api_key: str

    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None
    qdrant_collection: str = "agl_website"

    gemini_chat_model: str = "gemini-3-flash-preview"
    gemini_embedding_model: str = "gemini-embedding-001"

    embedding_dim: int = 3072
    scrape_data_dir: Path = PROJECT_ROOT / "data" / "website_scrape"
    top_k: int = 5

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        extra="ignore",
    )
