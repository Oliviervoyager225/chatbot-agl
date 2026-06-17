"""Terminal entrypoint for the AGL chatbot."""

import sys
import uuid

from langchain_core.messages import AIMessage, HumanMessage

from backend.agent.graph import get_compiled_graph
from backend.config import Settings
from backend.ingestion.indexer import sync_new_pages
from backend.logging_config import setup_logging

WELCOME = (
    "AGL Chatbot — Assistant virtuel pour Africa Global Logistics.\n"
    "Tapez votre question puis appuyez sur Entrée. (Ctrl+C pour quitter)\n"
)


def main() -> None:
    setup_logging()

    try:
        count = sync_new_pages(Settings())
        if count:
            print(f"Startup sync: indexed {count} new documents.")
    except Exception as exc:
        print(f"Startup sync failed ({exc}) — continuing without indexing.")

    graph = get_compiled_graph()
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    print(WELCOME)
    try:
        while True:
            question = input("You: ").strip()
            if not question:
                continue

            print("Assistant: ", end="", flush=True)
            for chunk, metadata in graph.stream(
                {"messages": [HumanMessage(content=question)]},
                config=config,
                stream_mode="messages",
            ):
                if metadata["langgraph_node"] != "agent":
                    continue
                if not isinstance(chunk, AIMessage):
                    continue
                content = chunk.content
                if isinstance(content, str):
                    text = content
                elif isinstance(content, list):
                    text = "".join(
                        part.get("text", "")
                        if isinstance(part, dict)
                        else str(part)
                        for part in content
                    )
                else:
                    continue
                if text:
                    print(text, end="", flush=True)
            print()
    except (KeyboardInterrupt, EOFError):
        print("\nAu revoir!")
        sys.exit(0)


if __name__ == "__main__":
    main()
