"""Tests for the Planner Agent."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.agents.planner.planner import PlannerAgent
from app.agents.schemas.agent_state import create_initial_state


@pytest.fixture
def planner():
    with patch("app.agents.planner.planner.get_llm") as mock_llm:
        mock_llm.return_value = MagicMock()
        agent = PlannerAgent()
        return agent


@pytest.fixture
def initial_state():
    return create_initial_state(customer_id=1, business_goal="Close the deal", user_id=10)


def test_planner_default_plan(planner):
    """Test the default fallback plan structure."""
    plan = planner._default_plan()
    assert "agents_to_call" in plan
    assert "execution_order" in plan
    assert "reasoning" in plan
    assert "crm_agent" in plan["agents_to_call"]
    assert "recommendation_agent" in plan["agents_to_call"]
    assert "memory_agent" in plan["agents_to_call"]
    assert len(plan["execution_order"]) == 7


def test_planner_validate_plan_adds_required_agents(planner):
    """Test that validation adds required agents."""
    plan = {"agents_to_call": ["knowledge_agent"], "execution_order": []}
    validated = planner._validate_plan(plan)
    assert "crm_agent" in validated["agents_to_call"]
    assert "recommendation_agent" in validated["agents_to_call"]
    assert "human_review_agent" in validated["agents_to_call"]
    assert "memory_agent" in validated["agents_to_call"]


def test_planner_validate_plan_keeps_existing_agents(planner):
    """Test that validation preserves user-specified agents."""
    plan = {
        "agents_to_call": ["knowledge_agent", "email_agent"],
        "execution_order": [],
    }
    validated = planner._validate_plan(plan)
    assert "knowledge_agent" in validated["agents_to_call"]
    assert "email_agent" in validated["agents_to_call"]


def test_planner_summarize_memory_empty(planner):
    """Test memory summarization with empty memory."""
    assert planner._summarize_memory([]) == "No previous memory"


def test_planner_summarize_memory_with_data(planner):
    """Test memory summarization with data."""
    memory = [
        {"memory_type": "execution_summary"},
        {"memory_type": "recommendations"},
        {"memory_type": "execution_summary"},
    ]
    summary = planner._summarize_memory(memory)
    assert "execution_summary" in summary
    assert "recommendations" in summary
    assert "Count: 3" in summary


@pytest.mark.asyncio
async def test_planner_run_uses_default_on_error(planner):
    """Test that planner falls back to default plan when LLM fails."""
    planner.llm = MagicMock()
    planner.llm.ainvoke = AsyncMock(side_effect=Exception("API error"))

    state = create_initial_state(1, "Test goal", 1)
    result = await planner.run(state)

    assert "planner_decisions" in result
    decisions = result["planner_decisions"]
    assert "crm_agent" in decisions.get("agents_to_call", [])
    assert "planner_agent" in result.get("executed_agents", [])
