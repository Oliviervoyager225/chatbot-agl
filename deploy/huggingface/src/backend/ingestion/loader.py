"""Load scraped JSON page data from disk."""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def load_pages(data_dir: Path) -> list[dict]:
    """Read all *.json files in *data_dir* and return a flat list of page dicts.

    Each returned dict has keys: title, text, link, source_file.
    """
    pages: list[dict] = []
    json_files = sorted(data_dir.glob("*.json"))

    if not json_files:
        logger.warning("No JSON files found in %s", data_dir)
        return pages

    for path in json_files:
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            logger.error("Failed to read %s: %s", path.name, exc)
            continue

        entries = raw if isinstance(raw, list) else [raw]
        for entry in entries:
            if not entry.get("text", "").strip():
                continue
            pages.append(
                {
                    "title": entry.get("title", ""),
                    "text": entry["text"],
                    "link": entry.get("link", ""),
                    "source_file": path.name,
                }
            )

    logger.info("Loaded %d pages from %d files", len(pages), len(json_files))
    return pages
