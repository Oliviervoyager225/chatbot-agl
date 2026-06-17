"""DuckDuckGo web search tool for the LangGraph agent."""

import logging

from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def web_search_tool(query: str) -> list[dict]:
    """Search the web for information not found in the AGL knowledge base.

    Use this tool ONLY when qdrant_search_tool returned empty or
    insufficient results.
    """
    search = DuckDuckGoSearchResults(
        output_format="list",
        num_results=5,
    )
    raw_results = search.invoke(query)

    if isinstance(raw_results, str):
        return [{"title": "", "url": "", "content": raw_results}]

    output = []
    for r in raw_results:
        output.append(
            {
                "title": r.get("title", ""),
                "url": r.get("link", ""),
                "content": r.get("snippet", ""),
            }
        )

    logger.info("Web search for '%s' returned %d results", query, len(output))
    return output
