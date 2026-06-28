"""Shared agent state schema for the LangGraph multi-agent pipeline."""

from __future__ import annotations

import uuid
from typing import TypedDict, Annotated
from operator import add


def merge_dicts(left: dict, right: dict) -> dict:
    """Merge two dicts, with right overwriting left on key conflicts."""
    merged = left.copy()
    merged.update(right)
    return merged


def merge_lists(left: list, right: list) -> list:
    """Append new items to existing list."""
    return left + right


class AgentState(TypedDict, total=False):
    """
    Shared state flowing through the entire LangGraph pipeline.
    Every agent reads from and writes to this state.
    """

    # ─── Input ───────────────────────────────────────────
    customer_id: int
    business_goal: str
    user_id: int
    execution_id: str

    # ─── CRM Data ────────────────────────────────────────
    customer: dict
    meetings: list[dict]
    emails: list[dict]
    support_tickets: list[dict]
    past_recommendations: list[dict]

    # ─── Analysis ────────────────────────────────────────
    transcript_analysis: dict
    email_analysis: dict
    support_analysis: dict

    # ─── Risk & Opportunity ──────────────────────────────
    risk_assessment: dict
    opportunity_assessment: dict

    # ─── RAG ─────────────────────────────────────────────
    retrieved_documents: list[dict]

    # ─── Recommendations ─────────────────────────────────
    recommendations: list[dict]

    # ─── Human Review Result ─────────────────────────────
    human_review_result: dict

    # ─── Memory ──────────────────────────────────────────
    memory: list[dict]
    memory_updated: bool

    # ─── Orchestration ───────────────────────────────────
    planner_decisions: dict
    executed_agents: Annotated[list[str], merge_lists]
    agent_errors: Annotated[dict, merge_dicts]
    agent_timings: Annotated[dict, merge_dicts]

    # ─── Output Metadata ─────────────────────────────────
    confidence: float
    evidence: list[str]


def create_initial_state(
    customer_id: int,
    business_goal: str,
    user_id: int,
) -> AgentState:
    """Create a fresh AgentState with defaults."""

    return AgentState(
        customer_id=customer_id,
        business_goal=business_goal,
        user_id=user_id,
        execution_id=str(uuid.uuid4()),
        customer={},
        meetings=[],
        emails=[],
        support_tickets=[],
        past_recommendations=[],
        transcript_analysis={},
        email_analysis={},
        support_analysis={},
        risk_assessment={},
        opportunity_assessment={},
        retrieved_documents=[],
        recommendations=[],
        human_review_result={},
        memory=[],
        memory_updated=False,
        planner_decisions={},
        executed_agents=[],
        agent_errors={},
        agent_timings={},
        confidence=0.0,
        evidence=[],
    )