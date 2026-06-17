"""Gemini chat model factory."""

from langchain_google_genai import ChatGoogleGenerativeAI

from backend.config import Settings


def get_llm(settings: Settings) -> ChatGoogleGenerativeAI:
    """Return a Gemini chat model instance."""
    return ChatGoogleGenerativeAI(
        model=settings.gemini_chat_model,
        google_api_key=settings.google_api_key,
    )
