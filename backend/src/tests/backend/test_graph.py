"""Tests for backend.agent.graph — three core scenarios."""

from unittest.mock import MagicMock, patch

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from backend.agent.graph import TOOLS, _agent_node
from backend.agent.prompts import SYSTEM_PROMPT


class TestAgentNode:
    """Unit tests for the agent node function."""

    def test_prepends_system_prompt(self):
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content="hello")
        state = {"messages": [HumanMessage(content="hi")]}

        _agent_node(state, mock_llm)

        call_args = mock_llm.invoke.call_args[0][0]
        assert isinstance(call_args[0], SystemMessage)
        assert call_args[0].content == SYSTEM_PROMPT

    def test_does_not_duplicate_system_prompt(self):
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content="hello")
        state = {
            "messages": [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content="hi"),
            ]
        }

        _agent_node(state, mock_llm)

        call_args = mock_llm.invoke.call_args[0][0]
        system_msgs = [m for m in call_args if isinstance(m, SystemMessage)]
        assert len(system_msgs) == 1


@patch("backend.agent.graph.get_llm")
@patch("backend.agent.graph.Settings")
def test_build_graph_creates_nodes(mock_settings_cls, mock_get_llm):
    mock_settings_cls.return_value = MagicMock(
        google_api_key="k",
        gemini_chat_model="gemini-3-flash-preview",
    )
    mock_llm = MagicMock()
    mock_llm.bind_tools.return_value = mock_llm
    mock_get_llm.return_value = mock_llm

    from backend.agent.graph import build_graph

    graph = build_graph()
    node_names = set(graph.nodes.keys())
    assert "agent" in node_names
    assert "tools" in node_names


def test_tools_list_has_both_tools():
    tool_names = {t.name for t in TOOLS}
    assert "qdrant_search_tool" in tool_names
    assert "web_search_tool" in tool_names
