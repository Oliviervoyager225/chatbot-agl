"""Gemini embeddings wrapper."""

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from backend.config import Settings


def get_embeddings(settings: Settings) -> GoogleGenerativeAIEmbeddings:
    """Return a Gemini embedding model instance."""
    return GoogleGenerativeAIEmbeddings(
        model=settings.gemini_embedding_model,
        google_api_key=settings.google_api_key,
    )
