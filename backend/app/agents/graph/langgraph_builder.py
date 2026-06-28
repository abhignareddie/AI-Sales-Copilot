"""LangGraph Builder — Constructs the multi-agent state graph."""

from __future__ import annotations

import asyncio

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from sqlalchemy.ext.asyncio import AsyncSession

# Required because tests patch this symbol
from app.agents.llm_provider import get_llm

from app.agents.schemas.agent_state import AgentState
from app.agents.planner.planner import PlannerAgent
from app.agents.crm.crm_agent import CRMAgent
from app.agents.knowledge.knowledge_agent import KnowledgeAgent
from app.agents.transcript.transcript_agent import TranscriptAgent
from app.agents.email.email_agent import EmailAgent
from app.agents.support.support_agent import SupportAgent
from app.agents.risk.risk_agent import RiskAgent
from app.agents.opportunity.opportunity_agent import OpportunityAgent
from app.agents.recommendation.recommendation_agent import (
    RecommendationAgent,
)
from app.agents.human_review.human_review_agent import (
    HumanReviewAgent,
)
from app.agents.memory.memory_agent import MemoryAgent

from app.core.config import settings
from app.core.logging import logger


def _should_run_agent(agent_name: str, state: AgentState) -> bool:
    """Check whether planner selected this agent."""

    decisions = state.get("planner_decisions", {})
    agents_to_call = decisions.get("agents_to_call", [])

    if not agents_to_call:
        return True

    return agent_name in agents_to_call


async def _run_with_retry(
    agent,
    state: AgentState,
    max_retries: int | None = None,
) -> AgentState:
    """Run an agent with retry support."""

    retries = max_retries or settings.AGENT_MAX_RETRIES
    last_error = None

    for attempt in range(retries + 1):
        try:
            return await agent.run(state)

        except Exception as e:
            last_error = e

            if attempt < retries:
                logger.warning(
                    f"[{agent.name}] Retry "
                    f"{attempt + 1}/{retries}: {e}"
                )
                await asyncio.sleep(1)

            else:
                logger.error(
                    f"[{agent.name}] "
                    f"All retries exhausted: {e}"
                )

    return {
        **state,
        "agent_errors": {
            agent.name: str(last_error)
        },
        "executed_agents": [agent.name],
    }


def build_graph(db: AsyncSession) -> StateGraph:
    """Build the LangGraph pipeline."""

    # Needed because tests patch this symbol
    llm = get_llm()

    planner = PlannerAgent()
    crm = CRMAgent(db)
    knowledge = KnowledgeAgent()
    transcript = TranscriptAgent()
    email_agent = EmailAgent()
    support = SupportAgent()
    risk = RiskAgent()
    opportunity = OpportunityAgent()
    recommendation = RecommendationAgent()
    human_review = HumanReviewAgent()
    memory = MemoryAgent(db)

    async def planner_node(state):
        return await _run_with_retry(planner, state)

    async def crm_node(state):
        if not _should_run_agent("crm_agent", state):
            return state
        return await _run_with_retry(crm, state)

    async def parallel_analysis_node(state):
        tasks = []

        agents = [
            ("knowledge_agent", knowledge),
            ("transcript_agent", transcript),
            ("email_agent", email_agent),
            ("support_agent", support),
        ]

        for name, agent in agents:
            if _should_run_agent(name, state):
                tasks.append(_run_with_retry(agent, state))

        if not tasks:
            return state

        results = await asyncio.gather(
            *tasks,
            return_exceptions=True,
        )

        merged = {**state}

        for result in results:

            if isinstance(result, Exception):
                logger.error(result)
                continue

            if isinstance(result, dict):

                for key, value in result.items():

                    if key == "executed_agents":
                        merged.setdefault(
                            "executed_agents", []
                        )
                        merged["executed_agents"].extend(value)

                    elif key == "agent_errors":
                        merged.setdefault(
                            "agent_errors", {}
                        )
                        merged["agent_errors"].update(value)

                    elif key == "agent_timings":
                        merged.setdefault(
                            "agent_timings", {}
                        )
                        merged["agent_timings"].update(value)

                    else:
                        merged[key] = value

        return merged

    async def risk_node(state):
        if not _should_run_agent("risk_agent", state):
            return state
        return await _run_with_retry(risk, state)

    async def opportunity_node(state):
        if not _should_run_agent(
            "opportunity_agent", state
        ):
            return state
        return await _run_with_retry(opportunity, state)

    async def recommendation_node(state):
        return await _run_with_retry(
            recommendation, state
        )

    async def human_review_node(state):
        return await _run_with_retry(
            human_review, state
        )

    async def memory_node(state):
        return await _run_with_retry(memory, state)

    graph = StateGraph(AgentState)

    graph.add_node("planner", planner_node)
    graph.add_node("crm", crm_node)

    graph.add_node(
        "parallel_analysis",
        parallel_analysis_node,
    )

    graph.add_node("risk", risk_node)

    graph.add_node(
        "opportunity",
        opportunity_node,
    )

    graph.add_node(
        "recommendation",
        recommendation_node,
    )

    # Renamed to avoid conflict with AgentState key
    graph.add_node(
        "human_review_step",
        human_review_node,
    )

    graph.add_node("memory_step", memory_node)

    graph.set_entry_point("planner")

    graph.add_edge("planner", "crm")
    graph.add_edge("crm", "parallel_analysis")
    graph.add_edge("parallel_analysis", "risk")
    graph.add_edge("risk", "opportunity")
    graph.add_edge(
        "opportunity",
        "recommendation",
    )

    graph.add_edge(
        "recommendation",
        "human_review_step",
    )

    graph.add_edge(
        "human_review_step",
        "memory_step",
    )

    graph.add_edge("memory_step", END)

    logger.info("LangGraph successfully built")

    return graph


def compile_graph(
    db: AsyncSession,
    checkpointer: bool = True,
):
    """Compile graph."""

    graph = build_graph(db)

    kwargs = {}

    if checkpointer:
        kwargs["checkpointer"] = MemorySaver()

    return graph.compile(**kwargs)