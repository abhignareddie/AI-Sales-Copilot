"""
AI Sales Copilot — Multi-Agent Platform

Enterprise-grade agent orchestration built with LangGraph.

Agents:
    - PlannerAgent: Orchestrates the pipeline
    - CRMAgent: Retrieves customer CRM data
    - KnowledgeAgent: RAG over enterprise knowledge base
    - TranscriptAgent: Analyzes meeting transcripts
    - EmailAgent: Analyzes email communications
    - SupportAgent: Analyzes support tickets
    - RiskAgent: Calculates deal risk scores
    - OpportunityAgent: Estimates win probability
    - RecommendationAgent: Generates Next Best Actions
    - HumanReviewAgent: Human approval workflow
    - MemoryAgent: Long-term customer memory
"""

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

__all__ = [
    "PlannerAgent",
    "CRMAgent",
    "KnowledgeAgent",
    "TranscriptAgent",
    "EmailAgent",
    "SupportAgent",
    "RiskAgent",
    "OpportunityAgent",
    "RecommendationAgent",
    "HumanReviewAgent",
    "MemoryAgent",
]
