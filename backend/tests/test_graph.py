"""Tests for the LangGraph builder and compilation."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from app.agents.schemas.agent_state import create_initial_state


def test_graph_build_succeeds():
    """Test that the graph builds without errors."""
    with patch("app.agents.graph.langgraph_builder.get_llm") as mock_llm:
        mock_llm.return_value = MagicMock()
        from app.agents.graph.langgraph_builder import build_graph
        mock_db = MagicMock()
        graph = build_graph(mock_db)
        assert graph is not None


def test_graph_compile_succeeds():
    """Test that the graph compiles without errors."""
    with patch("app.agents.graph.langgraph_builder.get_llm") as mock_llm:
        mock_llm.return_value = MagicMock()
        from app.agents.graph.langgraph_builder import compile_graph
        mock_db = MagicMock()
        compiled = compile_graph(mock_db, checkpointer=False)
        assert compiled is not None


def test_graph_has_all_nodes():
    """Test that the graph contains all expected nodes."""
    with patch("app.agents.graph.langgraph_builder.get_llm") as mock_llm:
        mock_llm.return_value = MagicMock()
        from app.agents.graph.langgraph_builder import build_graph
        mock_db = MagicMock()
        graph = build_graph(mock_db)

        expected_nodes = {
            "planner", "crm", "parallel_analysis",
            "risk", "opportunity", "recommendation",
            "human_review_step", "memory_step",
        }
        actual_nodes = set(graph.nodes.keys())
        assert expected_nodes.issubset(actual_nodes), (
            f"Missing nodes: {expected_nodes - actual_nodes}"
        )


def test_should_run_agent_with_empty_decisions():
    """Test that agents run when no planner decisions exist."""
    from app.agents.graph.langgraph_builder import _should_run_agent
    state = create_initial_state(1, "goal", 1)
    assert _should_run_agent("crm_agent", state) is True


def test_should_run_agent_with_decisions():
    """Test agent filtering based on planner decisions."""
    from app.agents.graph.langgraph_builder import _should_run_agent
    state = create_initial_state(1, "goal", 1)
    state["planner_decisions"] = {"agents_to_call": ["crm_agent", "risk_agent"]}
    assert _should_run_agent("crm_agent", state) is True
    assert _should_run_agent("email_agent", state) is False


@pytest.mark.asyncio
async def test_run_with_retry_succeeds():
    """Test retry wrapper with successful execution."""
    from app.agents.graph.langgraph_builder import _run_with_retry

    mock_agent = MagicMock()
    mock_agent.name = "test_agent"
    mock_agent.run = AsyncMock(return_value={"test": True})

    state = create_initial_state(1, "goal", 1)
    result = await _run_with_retry(mock_agent, state, max_retries=2)
    assert result["test"] is True
    mock_agent.run.assert_called_once()


@pytest.mark.asyncio
async def test_run_with_retry_retries_on_failure():
    """Test retry wrapper retries on failure."""
    from app.agents.graph.langgraph_builder import _run_with_retry

    mock_agent = MagicMock()
    mock_agent.name = "test_agent"
    mock_agent.run = AsyncMock(
        side_effect=[Exception("fail1"), {"test": True}]
    )

    state = create_initial_state(1, "goal", 1)
    result = await _run_with_retry(mock_agent, state, max_retries=1)
    assert result["test"] is True
    assert mock_agent.run.call_count == 2


@pytest.mark.asyncio
async def test_run_with_retry_exhausted():
    """Test retry wrapper when all retries fail."""
    from app.agents.graph.langgraph_builder import _run_with_retry

    mock_agent = MagicMock()
    mock_agent.name = "test_agent"
    mock_agent.run = AsyncMock(side_effect=Exception("always fails"))

    state = create_initial_state(1, "goal", 1)
    result = await _run_with_retry(mock_agent, state, max_retries=1)
    assert "test_agent" in result.get("agent_errors", {})
