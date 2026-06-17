"""LangGraph agent graph construction."""

import logging

from langchain_core.messages import SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from backend.agent.llm import get_llm
from backend.agent.prompts import SYSTEM_PROMPT
from backend.agent.state import AgentState
from backend.config import Settings
from backend.tools.qdrant_search import qdrant_search_tool
from backend.tools.web_search import web_search_tool

logger = logging.getLogger(__name__)

TOOLS = [qdrant_search_tool, web_search_tool]


def _agent_node(state: AgentState, llm):  # noqa: ANN001
    """Invoke the LLM with the current message history."""
    messages = state["messages"]
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
    response = llm.invoke(messages)
    return {"messages": [response]}


def build_graph(settings: Settings | None = None) -> StateGraph:
    """Construct the LangGraph StateGraph (uncompiled)."""
    settings = settings or Settings()
    llm = get_llm(settings).bind_tools(TOOLS)

    graph = StateGraph(AgentState)
    graph.add_node("agent", lambda state: _agent_node(state, llm))
    graph.add_node("tools", ToolNode(TOOLS))

    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", tools_condition, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")

    return graph


def get_compiled_graph(settings: Settings | None = None):  # noqa: ANN201
    """Return a compiled graph with memory checkpointing."""
    graph = build_graph(settings)
    return graph.compile(checkpointer=MemorySaver())
