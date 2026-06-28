"""LangGraph Builder — Constructs the multi-agent state graph with conditional routing."""

from __future__ import annotations

import asyncio
from typing import Literal

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.schemas.agent_state import AgentState
from app.agents.planner.planner import PlannerAgent
from app.agents.crm.crm_agent import CRMAgent
from app.agents.knowledge.knowledge_agent import KnowledgeAgent
from app.agents.transcript.transcript_agent import TranscriptAgent
from app.agents.email.email_agent import EmailAgent
from app.agents.support.support_agent import SupportAgent
from app.agents.risk.risk_agent import RiskAgent
from app.agents.opportunity.opportunity_agent import OpportunityAgent
from app.agents.recommendation.recommendation_agent import RecommendationAgent
from app.agents.human_review.human_review_agent import HumanReviewAgent
from app.agents.memory.memory_agent import MemoryAgent
from app.core.config import settings
from app.core.logging import logger


def _should_run_agent(agent_name: str, state: AgentState) -> bool:
    """Check if planner decided this agent should run."""
    decisions = state.get("planner_decisions", {})
    agents_to_call = decisions.get("agents_to_call", [])
    # If no planner decisions, run everything
    if not agents_to_call:
        return True
    return agent_name in agents_to_call


async def _run_with_retry(agent, state: AgentState, max_retries: int | None = None) -> AgentState:
    """Run an agent with retry logic."""
    retries = max_retries or settings.AGENT_MAX_RETRIES
    last_error = None
    for attempt in range(retries + 1):
        try:
            return await agent.run(state)
        except Exception as e:
            last_error = e
            if attempt < retries:
                logger.warning(f"[{agent.name}] Retry {attempt + 1}/{retries}: {e}")
                await asyncio.sleep(1)
            else:
                logger.error(f"[{agent.name}] All {retries} retries exhausted: {e}")
    return {
        **state,
        "agent_errors": {agent.name: str(last_error)},
        "executed_agents": [agent.name],
    }


def build_graph(db: AsyncSession) -> StateGraph:
    """
    Build the complete LangGraph state graph.

    Flow:
        Planner → CRM → [Knowledge, Transcript, Email, Support] (parallel)
        → Risk → Opportunity → Recommendation → Human Review → Memory
    """

    # Instantiate all agents
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

    # ─── Node functions ───────────────────────────────────

    async def planner_node(state: AgentState) -> AgentState:
        return await _run_with_retry(planner, state)

    async def crm_node(state: AgentState) -> AgentState:
        if not _should_run_agent("crm_agent", state):
            return state
        return await _run_with_retry(crm, state)

    async def knowledge_node(state: AgentState) -> AgentState:
        if not _should_run_agent("knowledge_agent", state):
            return state
        return await _run_with_retry(knowledge, state)

    async def transcript_node(state: AgentState) -> AgentState:
        if not _should_run_agent("transcript_agent", state):
            return state
        return await _run_with_retry(transcript, state)

    async def email_node(state: AgentState) -> AgentState:
        if not _should_run_agent("email_agent", state):
            return state
        return await _run_with_retry(email_agent, state)

    async def support_node(state: AgentState) -> AgentState:
        if not _should_run_agent("support_agent", state):
            return state
        return await _run_with_retry(support, state)

    async def risk_node(state: AgentState) -> AgentState:
        if not _should_run_agent("risk_agent", state):
            return state
        return await _run_with_retry(risk, state)

    async def opportunity_node(state: AgentState) -> AgentState:
        if not _should_run_agent("opportunity_agent", state):
            return state
        return await _run_with_retry(opportunity, state)

    async def recommendation_node(state: AgentState) -> AgentState:
        return await _run_with_retry(recommendation, state)

    async def human_review_node(state: AgentState) -> AgentState:
        return await _run_with_retry(human_review, state)

    async def memory_node(state: AgentState) -> AgentState:
        return await _run_with_retry(memory, state)

    # ─── Parallel analysis fan-out/fan-in ─────────────────

    async def parallel_analysis_node(state: AgentState) -> AgentState:
        """Run knowledge, transcript, email, and support agents in parallel."""
        tasks = []
        agents = [
            ("knowledge_agent", knowledge),
            ("transcript_agent", transcript),
            ("email_agent", email_agent),
            ("support_agent", support),
        ]

        for agent_name, agent in agents:
            if _should_run_agent(agent_name, state):
                tasks.append(_run_with_retry(agent, state))

        if not tasks:
            return state

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Merge all results into state
        merged = {**state}
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Parallel agent failed: {result}")
                continue
            if isinstance(result, dict):
                for key, value in result.items():
                    if key == "executed_agents":
                        merged.setdefault("executed_agents", [])
                        if isinstance(merged["executed_agents"], list):
                            merged["executed_agents"] = list(merged["executed_agents"]) + list(value)
                    elif key == "agent_errors":
                        merged.setdefault("agent_errors", {})
                        merged["agent_errors"].update(value)
                    elif key == "agent_timings":
                        merged.setdefault("agent_timings", {})
                        merged["agent_timings"].update(value)
                    elif value:  # Only overwrite if non-empty
                        merged[key] = value

        return merged

    # ─── Build Graph ──────────────────────────────────────

    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("planner", planner_node)
    graph.add_node("crm", crm_node)
    graph.add_node("parallel_analysis", parallel_analysis_node)
    graph.add_node("risk", risk_node)
    graph.add_node("opportunity", opportunity_node)
    graph.add_node("recommendation", recommendation_node)
    graph.add_node("human_review_node", human_review_node)
    graph.add_node("memory_node", memory_node)

    # Set entry point
    graph.set_entry_point("planner")

    # Add edges — sequential pipeline with parallel analysis fan-out
    graph.add_edge("planner", "crm")
    graph.add_edge("crm", "parallel_analysis")
    graph.add_edge("parallel_analysis", "risk")
    graph.add_edge("risk", "opportunity")
    graph.add_edge("opportunity", "recommendation")
    graph.add_edge("recommendation", "human_review_node")
    graph.add_edge("human_review_node", "memory_node")
    graph.add_edge("memory_node", END)

    logger.info("LangGraph built: planner → crm → [parallel analysis] → risk → opportunity → recommendation → human_review → memory")
    return graph


def compile_graph(db: AsyncSession, checkpointer: bool = True):
    """Compile the graph with optional checkpointing."""
    graph = build_graph(db)
    kwargs = {}
    if checkpointer:
        kwargs["checkpointer"] = MemorySaver()
    return graph.compile(**kwargs)
