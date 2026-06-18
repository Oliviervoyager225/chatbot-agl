"""Centralized logging configuration."""

import logging
import os


def setup_logging(level: str | None = None) -> None:
    """Configure stdlib logging for the backend package."""
    log_level = level or os.getenv("LOG_LEVEL", "INFO")
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    )
