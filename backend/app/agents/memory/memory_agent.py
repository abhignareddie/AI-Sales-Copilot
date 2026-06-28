"""Memory Agent — Stores and retrieves long-term customer memory."""

from typing import Any
import json
from sqlalchemy.ext.asyncio import AsyncSession

from app.framework.registry import AgentRegistry
from app.framework.interfaces import BaseAgent
from app.agents.base_agent import BaseAgent as LegacyBaseAgent
from app.agents.schemas.agent_state import AgentState
from app.agents.tools.memory_tool import MemoryTool
from app.core.logging import logger


@AgentRegistry.register("memory_agent")
class MemoryAgent(BaseAgent, LegacyBaseAgent):
    """
    Manages long-term customer memory.
    Stores meeting summaries, customer preferences, approved/rejected recommendations,
    and conversation history. Retrieves memory at pipeline start for context.
    """

    name = "memory_agent"
    description = "Stores and retrieves long-term customer memory"

    def __init__(self, db: AsyncSession, *args, **kwargs):
        LegacyBaseAgent.__init__(self, *args, **kwargs)
        self.memory_tool = MemoryTool(db)

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        customer_id = state.get("customer_id", 0)
        execution_id = state.get("execution_id", "")

        # Store execution summary as memory
        summary = self._build_execution_summary(state)

        try:
            await self.memory_tool.store_memory(
                customer_id=customer_id,
                memory_type="execution_summary",
                memory_data={
                    "execution_id": execution_id,
                    "business_goal": state.get("business_goal", ""),
                    "summary": summary,
                },
            )

            # Store recommendations as memory
            recommendations = state.get("recommendations", [])
            if recommendations:
                await self.memory_tool.store_memory(
                    customer_id=customer_id,
                    memory_type="recommendations",
                    memory_data={
                        "execution_id": execution_id,
                        "count": len(recommendations),
                        "recommendations": [
                            {
                                "action": r.get("action", ""),
                                "priority": r.get("priority", 0),
                                "confidence": r.get("confidence", 0),
                            }
                            for r in recommendations[:5]
                        ],
                    },
                )

            # Store risk/opportunity scores
            risk = state.get("risk_assessment", {})
            opportunity = state.get("opportunity_assessment", {})
            if risk or opportunity:
                await self.memory_tool.store_memory(
                    customer_id=customer_id,
                    memory_type="assessment_snapshot",
                    memory_data={
                        "execution_id": execution_id,
                        "risk_level": risk.get("risk_level", "unknown"),
                        "risk_score": risk.get("overall_risk_score", 0),
                        "opportunity_score": opportunity.get("overall_opportunity_score", 0),
                        "win_probability": opportunity.get("win_probability", {}).get("score", 0),
                    },
                )

            logger.info(f"[memory_agent] Stored execution memory for customer {customer_id}")
            return {**state, "memory_updated": True}

        except Exception as e:
            logger.error(f"[memory_agent] Failed to store memory: {e}")
            return {**state, "memory_updated": False}

    async def load_memory(self, customer_id: int) -> list[dict]:
        """Load all memory for a customer (called at pipeline start)."""
        try:
            memories = await self.memory_tool.retrieve_all_memory(customer_id)
            logger.info(f"[memory_agent] Loaded {len(memories)} memory records for customer {customer_id}")
            return memories
        except Exception as e:
            logger.warning(f"[memory_agent] Failed to load memory: {e}")
            return []

    def _build_execution_summary(self, state: AgentState) -> dict:
        """Build a summary of the current execution."""
        return {
            "executed_agents": state.get("executed_agents", []),
            "confidence": state.get("confidence", 0),
            "risk_level": state.get("risk_assessment", {}).get("risk_level", "unknown"),
            "recommendations_count": len(state.get("recommendations", [])),
            "errors": list(state.get("agent_errors", {}).keys()),
        }
