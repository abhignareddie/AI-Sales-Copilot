"""Opportunity Agent — Estimates win probability and expansion opportunities."""

from typing import Any
import json
from app.framework.registry import AgentRegistry
from app.framework.interfaces import BaseAgent
from app.agents.base_agent import BaseAgent as LegacyBaseAgent
from app.agents.schemas.agent_state import AgentState
from app.core.logging import logger

OPPORTUNITY_SYSTEM_PROMPT = """You are an expert B2B sales opportunity analyst.
Analyze all available data and estimate opportunity scores.

Return valid JSON:
{
    "overall_opportunity_score": 0.0-1.0,
    "win_probability": {"score": 0.0-1.0, "factors": ["positive indicators"], "blockers": ["obstacles"]},
    "upsell_opportunity": {"score": 0.0-1.0, "products": ["potential upsell products"], "reasoning": "why"},
    "cross_sell_opportunity": {"score": 0.0-1.0, "products": ["potential cross-sell products"], "reasoning": "why"},
    "renewal_chance": {"score": 0.0-1.0, "factors": ["retention indicators"]},
    "expansion_opportunity": {"score": 0.0-1.0, "areas": ["growth areas"], "reasoning": "why"},
    "deal_value_estimate": "estimated deal value range",
    "next_milestone": "next critical milestone in the deal",
    "key_strengths": ["competitive advantages"],
    "recommended_approach": "best strategy to maximize opportunity"
}"""


@AgentRegistry.register("opportunity_agent")
class OpportunityAgent(BaseAgent, LegacyBaseAgent):
    """Estimates win probability, upsell, cross-sell, and expansion opportunity."""

    name = "opportunity_agent"
    description = "Estimates opportunity scores and growth potential"
    system_prompt = OPPORTUNITY_SYSTEM_PROMPT

    def __init__(self, *args, **kwargs):
        LegacyBaseAgent.__init__(self)

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        customer = state.get("customer", {})
        risk = state.get("risk_assessment", {})
        transcript = state.get("transcript_analysis", {})
        email = state.get("email_analysis", {})
        docs = state.get("retrieved_documents", [])

        prompt = f"""Analyze opportunities for this customer:

CUSTOMER PROFILE:
{json.dumps(customer, indent=2, default=str)}

RISK ASSESSMENT:
{json.dumps(risk, indent=2, default=str)}

TRANSCRIPT INSIGHTS:
{json.dumps(transcript, indent=2, default=str)}

EMAIL INSIGHTS:
{json.dumps(email, indent=2, default=str)}

RELEVANT KNOWLEDGE:
{json.dumps([d.get('content', '')[:500] for d in docs[:3]], indent=2)}"""

        try:
            response = await self.invoke_llm(prompt)
            assessment = self.parse_json_response(response)
        except Exception as e:
            logger.warning(f"[opportunity_agent] LLM failed: {e}")
            assessment = self._heuristic_opportunity(customer, risk)

        logger.info(
            f"[opportunity_agent] Win probability: "
            f"{assessment.get('win_probability', {}).get('score', 'N/A')}"
        )

        return {**state, "opportunity_assessment": assessment}

    def _heuristic_opportunity(self, customer: dict, risk: dict) -> dict:
        """Fallback heuristic."""
        health = customer.get("health_score", 50) / 100
        risk_score = risk.get("overall_risk_score", 0.5)
        win = round(health * (1 - risk_score * 0.5), 2)
        return {
            "overall_opportunity_score": win,
            "win_probability": {"score": win, "factors": ["health score"], "blockers": []},
            "upsell_opportunity": {"score": 0.3, "products": [], "reasoning": "Insufficient data"},
            "cross_sell_opportunity": {"score": 0.3, "products": [], "reasoning": "Insufficient data"},
            "renewal_chance": {"score": health, "factors": ["health score based"]},
            "expansion_opportunity": {"score": 0.3, "areas": [], "reasoning": "Insufficient data"},
            "deal_value_estimate": "Unable to estimate",
            "next_milestone": "Follow-up meeting",
            "key_strengths": [],
            "recommended_approach": "Gather more information",
        }
