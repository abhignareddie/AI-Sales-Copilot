"""Tests for AgentState schema."""

import pytest
from app.agents.schemas.agent_state import AgentState, create_initial_state


def test_create_initial_state():
    """Test creating initial state with defaults."""
    state = create_initial_state(
        customer_id=1,
        business_goal="Test goal",
        user_id=10,
    )

    assert state["customer_id"] == 1
    assert state["business_goal"] == "Test goal"
    assert state["user_id"] == 10
    assert state["execution_id"]  # UUID generated
    assert state["customer"] == {}
    assert state["meetings"] == []
    assert state["emails"] == []
    assert state["support_tickets"] == []
    assert state["past_recommendations"] == []
    assert state["recommendations"] == []
    assert state["memory"] == []
    assert state["memory_updated"] is False
    assert state["executed_agents"] == []
    assert state["agent_errors"] == {}
    assert state["agent_timings"] == {}
    assert state["confidence"] == 0.0
    assert state["evidence"] == []


def test_state_is_typed_dict():
    """Test that AgentState behaves like a dict."""
    state = create_initial_state(1, "goal", 1)
    assert isinstance(state, dict)
    state["customer"] = {"id": 1, "name": "Test"}
    assert state["customer"]["id"] == 1


def test_state_execution_id_is_unique():
    """Test that each state gets a unique execution ID."""
    state1 = create_initial_state(1, "goal1", 1)
    state2 = create_initial_state(1, "goal2", 1)
    assert state1["execution_id"] != state2["execution_id"]


def test_state_merge_dicts():
    """Test the merge_dicts reducer."""
    from app.agents.schemas.agent_state import merge_dicts

    left = {"a": 1, "b": 2}
    right = {"b": 3, "c": 4}
    result = merge_dicts(left, right)
    assert result == {"a": 1, "b": 3, "c": 4}
    # Original dicts unchanged
    assert left == {"a": 1, "b": 2}


def test_state_merge_lists():
    """Test the merge_lists reducer."""
    from app.agents.schemas.agent_state import merge_lists

    result = merge_lists(["a", "b"], ["c", "d"])
    assert result == ["a", "b", "c", "d"]
