"""Base Agent — Abstract base for all specialized agents."""

from __future__ import annotations

import time
import json
from abc import ABC, abstractmethod
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from app.agents.llm_provider import get_llm
from app.agents.schemas.agent_state import AgentState
from app.core.logging import logger


class BaseAgent(ABC):
    """
    Abstract base class for all specialized agents.
    Provides LLM invocation, error handling, timing, and structured output parsing.
    """

    name: str = "base_agent"
    description: str = "Base agent"
    system_prompt: str = "You are a helpful AI assistant."

    def __init__(self, temperature: float = 0.2):
        self.llm = get_llm(temperature=temperature)
        self.temperature = temperature

    async def run(self, state: AgentState) -> AgentState:
        """Execute the agent with timing and error handling."""
        start = time.time()
        logger.info(f"[{self.name}] Starting execution...")

        try:
            result_state = await self.execute(state)
            elapsed = round(time.time() - start, 3)
            result_state["agent_timings"] = {self.name: elapsed}
            result_state["executed_agents"] = [self.name]
            logger.info(f"[{self.name}] Completed in {elapsed}s")
            return result_state
        except Exception as e:
            elapsed = round(time.time() - start, 3)
            logger.error(f"[{self.name}] Failed after {elapsed}s: {e}")
            return {
                **state,
                "agent_errors": {self.name: str(e)},
                "agent_timings": {self.name: elapsed},
                "executed_agents": [self.name],
            }

    @abstractmethod
    async def execute(self, state: AgentState) -> AgentState:
        """Override in subclass to implement agent logic."""
        ...

    async def invoke_llm(
        self,
        prompt: str,
        system_prompt: str | None = None,
    ) -> str:
        """Invoke the LLM via centralized LLMFactory."""
        from app.services.llm_factory import LLMFactory
        llm_service = LLMFactory.get_llm()
        if hasattr(llm_service, "generate"):
            return await llm_service.generate(prompt, system_prompt or self.system_prompt)
        
        messages = [
            SystemMessage(content=system_prompt or self.system_prompt),
            HumanMessage(content=prompt),
        ]
        response = await self.llm.ainvoke(messages)
        return response.content

    def parse_json_response(self, text: str) -> dict | list:
        """Extract JSON from LLM response (handles markdown code blocks)."""
        cleaned = text.strip()
        # Remove markdown code blocks if present
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Try to find JSON in the response
            start = cleaned.find("{")
            end = cleaned.rfind("}") + 1
            if start >= 0 and end > start:
                try:
                    return json.loads(cleaned[start:end])
                except json.JSONDecodeError:
                    pass
            # Try array
            start = cleaned.find("[")
            end = cleaned.rfind("]") + 1
            if start >= 0 and end > start:
                try:
                    return json.loads(cleaned[start:end])
                except json.JSONDecodeError:
                    pass

            logger.warning(f"[{self.name}] Failed to parse JSON from LLM response")
            return {"raw_response": text}
