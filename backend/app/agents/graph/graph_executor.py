"""Graph Executor — Runs the compiled LangGraph pipeline and returns structured output."""

from __future__ import annotations

import time
import uuid
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.schemas.agent_state import AgentState, create_initial_state
from app.agents.graph.langgraph_builder import compile_graph
from app.agents.memory.memory_agent import MemoryAgent
from app.agents.tools.recommendation_tool import RecommendationTool
from app.core.logging import logger


class GraphExecutor:
    """
    Orchestrates the entire multi-agent pipeline.
    Handles memory pre-loading, graph execution, recommendation persistence,
    streaming, and structured output formatting.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.memory_agent = MemoryAgent(db)
        self.recommendation_tool = RecommendationTool(db)

    async def execute(
        self,
        customer_id: int,
        business_goal: str,
        user_id: int,
    ) -> dict:
        """
        Execute the full agent pipeline for a customer.

        Returns structured JSON with all results, timing, and observability data.
        """
        start_time = time.time()
        execution_id = str(uuid.uuid4())

        logger.info(
            f"[executor] Starting pipeline: customer={customer_id}, "
            f"goal='{business_goal[:50]}...', execution={execution_id}"
        )

        # 1. Load customer memory
        memory = await self.memory_agent.load_memory(customer_id)

        # 2. Create initial state
        state = create_initial_state(
            customer_id=customer_id,
            business_goal=business_goal,
            user_id=user_id,
        )
        state["execution_id"] = execution_id
        state["memory"] = memory

        # 3. Compile and run the graph
        graph = compile_graph(self.db, checkpointer=True)

        config = {"configurable": {"thread_id": execution_id}}

        try:
            final_state = await graph.ainvoke(state, config=config)
        except Exception as e:
            logger.error(f"[executor] Pipeline failed: {e}")
            final_state = {
                **state,
                "agent_errors": {"graph_executor": str(e)},
            }

        # 4. Persist recommendations to DB
        recommendations = final_state.get("recommendations", [])
        if recommendations:
            try:
                await self.recommendation_tool.save_recommendations(
                    customer_id=customer_id,
                    recommendations=recommendations,
                )
            except Exception as e:
                logger.warning(f"[executor] Failed to save recommendations: {e}")

        # 5. Format structured output
        elapsed = round(time.time() - start_time, 3)
        output = self._format_output(final_state, elapsed, execution_id)

        logger.info(
            f"[executor] Pipeline completed in {elapsed}s: "
            f"{len(recommendations)} recommendations generated"
        )

        return output

    async def execute_streaming(
        self,
        customer_id: int,
        business_goal: str,
        user_id: int,
    ) -> AsyncGenerator[dict, None]:
        """
        Execute the pipeline with streaming intermediate results.
        Yields progress updates as each agent completes.
        """
        start_time = time.time()
        execution_id = str(uuid.uuid4())

        # Load memory
        memory = await self.memory_agent.load_memory(customer_id)

        state = create_initial_state(
            customer_id=customer_id,
            business_goal=business_goal,
            user_id=user_id,
        )
        state["execution_id"] = execution_id
        state["memory"] = memory

        graph = compile_graph(self.db, checkpointer=True)
        config = {"configurable": {"thread_id": execution_id}}

        yield {
            "type": "progress",
            "agent": "executor",
            "message": "Pipeline started",
            "execution_id": execution_id,
        }

        try:
            async for event in graph.astream(state, config=config):
                for node_name, node_output in event.items():
                    elapsed = round(time.time() - start_time, 3)
                    yield {
                        "type": "agent_complete",
                        "agent": node_name,
                        "elapsed": elapsed,
                        "executed_agents": node_output.get("executed_agents", []),
                        "has_errors": bool(node_output.get("agent_errors")),
                    }

                    # Persist recommendations when recommendation agent completes
                    if node_name == "recommendation" and node_output.get("recommendations"):
                        try:
                            await self.recommendation_tool.save_recommendations(
                                customer_id=customer_id,
                                recommendations=node_output["recommendations"],
                            )
                        except Exception:
                            pass

                    final_state = node_output

        except Exception as e:
            yield {
                "type": "error",
                "agent": "executor",
                "message": str(e),
            }
            final_state = {**state, "agent_errors": {"executor": str(e)}}

        elapsed = round(time.time() - start_time, 3)
        yield {
            "type": "complete",
            "result": self._format_output(final_state, elapsed, execution_id),
        }

    def _format_output(
        self,
        state: AgentState,
        execution_time: float,
        execution_id: str,
    ) -> dict:
        """Format the final structured JSON output."""
        customer = state.get("customer", {})
        risk = state.get("risk_assessment", {})
        opportunity = state.get("opportunity_assessment", {})

        return {
            "execution_id": execution_id,
            "execution_time": execution_time,

            "planner_reasoning": state.get("planner_decisions", {}).get("reasoning", ""),

            "executed_agents": state.get("executed_agents", []),
            "agent_timings": state.get("agent_timings", {}),
            "agent_errors": state.get("agent_errors", {}),

            "customer_summary": {
                "company": customer.get("company_name", "Unknown"),
                "contact": customer.get("contact_person", "Unknown"),
                "stage": customer.get("current_stage", "Unknown"),
                "health_score": customer.get("health_score", 0),
                "industry": customer.get("industry", "Unknown"),
                "revenue": customer.get("annual_revenue"),
            },

            "risk": {
                "level": risk.get("risk_level", "unknown"),
                "score": risk.get("overall_risk_score", 0),
                "top_factors": risk.get("top_risk_factors", []),
                "deal_risk": risk.get("deal_risk", {}),
                "churn_risk": risk.get("churn_risk", {}),
            },

            "opportunity": {
                "score": opportunity.get("overall_opportunity_score", 0),
                "win_probability": opportunity.get("win_probability", {}).get("score", 0),
                "upsell": opportunity.get("upsell_opportunity", {}).get("score", 0),
                "cross_sell": opportunity.get("cross_sell_opportunity", {}).get("score", 0),
            },

            "recommendations": state.get("recommendations", []),
            "confidence": state.get("confidence", 0),
            "evidence": state.get("evidence", []),

            "retrieved_documents": [
                {
                    "source": d.get("source", ""),
                    "similarity": d.get("similarity_score", 0),
                    "content_preview": d.get("content", "")[:200],
                }
                for d in state.get("retrieved_documents", [])
            ],

            "memory_used": len(state.get("memory", [])),
            "memory_updated": state.get("memory_updated", False),

            "human_review": state.get("human_review", {}),
        }
