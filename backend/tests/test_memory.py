"""Tests for Memory Tool and Agent."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from app.agents.schemas.agent_state import create_initial_state


@pytest.mark.asyncio
async def test_memory_tool_store(db_session):
    """Test storing a memory record."""
    from app.agents.tools.memory_tool import MemoryTool

    tool = MemoryTool(db_session)
    result = await tool.store_memory(
        customer_id=1,
        memory_type="test_memory",
        memory_data={"key": "value", "score": 0.8},
    )

    assert result["memory_type"] == "test_memory"
    assert result["memory_data"]["key"] == "value"
    assert "id" in result
    assert "created_at" in result


@pytest.mark.asyncio
async def test_memory_tool_retrieve(db_session):
    """Test retrieving memory records."""
    from app.agents.tools.memory_tool import MemoryTool

    tool = MemoryTool(db_session)

    # Store two records
    await tool.store_memory(1, "type_a", {"data": "first"})
    await tool.store_memory(1, "type_b", {"data": "second"})

    # Retrieve all
    results = await tool.retrieve_memory(1)
    assert len(results) >= 2

    # Retrieve by type
    results = await tool.retrieve_memory(1, memory_type="type_a")
    assert all(r["memory_type"] == "type_a" for r in results)


@pytest.mark.asyncio
async def test_memory_tool_retrieve_all(db_session):
    """Test retrieving all memory for a customer."""
    from app.agents.tools.memory_tool import MemoryTool

    tool = MemoryTool(db_session)
    await tool.store_memory(1, "summary", {"test": True})

    all_memories = await tool.retrieve_all_memory(1)
    assert isinstance(all_memories, list)


@pytest.mark.asyncio
async def test_memory_agent_execute():
    """Test memory agent stores execution data."""
    state = create_initial_state(1, "Test goal", 10)
    state["recommendations"] = [
        {"action": "Follow up", "priority": 1, "confidence": 0.8}
    ]
    state["risk_assessment"] = {"risk_level": "medium", "overall_risk_score": 0.5}
    state["opportunity_assessment"] = {"overall_opportunity_score": 0.7}

    with patch("app.agents.llm_provider.get_llm") as mock_llm:
        mock_llm.return_value = MagicMock()

        mock_db = MagicMock()
        mock_db.add = MagicMock()
        mock_db.flush = AsyncMock()
        mock_db.refresh = AsyncMock()
        mock_db.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))))

        from app.agents.memory.memory_agent import MemoryAgent
        agent = MemoryAgent(mock_db)

        # Mock the memory tool
        agent.memory_tool.store_memory = AsyncMock(return_value={
            "id": 1, "memory_type": "test", "memory_data": {}, "created_at": None
        })

        result = await agent.run(state)
        assert "memory_agent" in result.get("executed_agents", [])
