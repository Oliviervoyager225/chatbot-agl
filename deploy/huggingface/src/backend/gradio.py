"""Gradio web UI entrypoint for the AGL chatbot."""

import logging
import uuid
from collections.abc import Generator

import gradio as gr
from langchain_core.messages import AIMessage, HumanMessage

from backend.agent.graph import get_compiled_graph
from backend.config import Settings
from backend.ingestion.indexer import sync_new_pages
from backend.logging_config import setup_logging

logger = logging.getLogger(__name__)


def _create_app() -> gr.Blocks:
    """Build and return the Gradio application."""
    setup_logging()

    try:
        count = sync_new_pages(Settings())
        if count:
            logger.info("Startup sync: indexed %d new documents", count)
    except Exception:
        logger.exception("Startup sync failed — continuing without indexing")

    graph = get_compiled_graph()

    with gr.Blocks(title="AGL Chatbot") as demo:
        gr.Markdown(
            "# AGL Chatbot\n"
            "Assistant virtuel pour **Africa Global Logistics**. "
            "Posez vos questions sur les services, la logistique et les activités d'AGL."
        )

        thread_state = gr.State(value=str(uuid.uuid4()))

        chatbot = gr.Chatbot(
            height=500,
            placeholder="",
        )
        msg = gr.Textbox(
            placeholder="Posez votre question ici...",
            show_label=False,
            scale=7,
        )

        examples = gr.Examples(
            examples=[
                "Quels sont les services proposés par AGL ?",
                "What is Africa Global Logistics?",
                "Quelles sont les concessions portuaires d'AGL ?",
            ],
            inputs=msg,
        )

        def user_message(message: str, history: list[dict]):
            return "", history + [{"role": "user", "content": message}]

        def bot_response(
            history: list[dict], thread_id: str
        ) -> Generator[tuple[list[dict], str], None, None]:
            user_msg = history[-1]["content"]
            config = {"configurable": {"thread_id": thread_id}}
            history.append({"role": "assistant", "content": ""})

            for chunk, metadata in graph.stream(
                {"messages": [HumanMessage(content=user_msg)]},
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
                    history[-1]["content"] += text
                    yield history, thread_id

        msg.submit(
            user_message,
            inputs=[msg, chatbot],
            outputs=[msg, chatbot],
            queue=False,
        ).then(
            bot_response,
            inputs=[chatbot, thread_state],
            outputs=[chatbot, thread_state],
        )

    return demo


def main() -> None:
    """Launch the Gradio web UI."""
    app = _create_app()
    app.launch(server_name="0.0.0.0",share=True)


if __name__ == "__main__":
    main()
