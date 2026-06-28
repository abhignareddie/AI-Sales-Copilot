"""Tests for the Enterprise Agentic AI Framework Core component."""

import pytest
from app.framework.registry import AgentRegistry, ToolRegistry, PromptRegistry
from app.framework.interfaces import BaseAgent, BaseTool
from app.framework.llm_provider import MockLLMProvider, LLMFactory
from app.framework.vector_store import MockVectorStore, VectorStoreFactory
from app.framework.memory_provider import MockMemoryProvider


def test_agent_registry():
    """Test registering and resolving agents."""
    @AgentRegistry.register("test_dummy_agent")
    class DummyAgent(BaseAgent):
        name = "test_dummy_agent"
        description = "dummy test"
        async def execute(self, state):
            return state

    assert "test_dummy_agent" in AgentRegistry.list_registered()
    agent_cls = AgentRegistry.get("test_dummy_agent")
    assert agent_cls == DummyAgent


def test_tool_registry():
    """Test registering and resolving tools."""
    @ToolRegistry.register("test_dummy_tool")
    class DummyTool(BaseTool):
        name = "test_dummy_tool"
        description = "dummy tool"
        async def execute(self, **kwargs):
            return "executed"

    assert "test_dummy_tool" in ToolRegistry.list_registered()
    tool_cls = ToolRegistry.get("test_dummy_tool")
    assert tool_cls == DummyTool


def test_prompt_registry():
    """Test registering and formatting prompts."""
    PromptRegistry.register("welcome_prompt", "Hello {name}, welcome to {domain}!")
    
    formatted = PromptRegistry.get("welcome_prompt", name="Alice", domain="Healthcare")
    assert formatted == "Hello Alice, welcome to Healthcare!"

    # Unformatted return
    raw = PromptRegistry.get("welcome_prompt")
    assert raw == "Hello {name}, welcome to {domain}!"


@pytest.mark.asyncio
async def test_mock_llm_provider():
    """Test Mock LLM responds correctly."""
    provider = MockLLMProvider()
    response = await provider.generate("hello world", system_prompt="This is a risk_agent prompt")
    assert "risk_level" in response


@pytest.mark.asyncio
async def test_mock_vector_store():
    """Test mock vector store search."""
    store = MockVectorStore()
    store.add_document("doc_test", "This is an custom discount playbook.", {"document_type": "playbook"})
    
    results = store.search("discount playbook")
    assert len(results) > 0
    assert "custom discount" in results[0]["content"]


@pytest.mark.asyncio
async def test_mock_memory_provider():
    """Test mock memory provider storage and retrieval."""
    provider = MockMemoryProvider()
    
    # Store
    await provider.store("cust_1", "history", {"event": "call_ended"})
    await provider.store("cust_1", "history", {"event": "email_sent"})
    
    # Retrieve
    memories = await provider.retrieve("cust_1")
    assert len(memories) == 2
    assert memories[0]["memory_data"]["event"] == "email_sent" # lifo order
