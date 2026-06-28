"""Risk Agent — Calculates multi-dimensional deal risk scores."""

from typing import Any
import json
from app.framework.registry import AgentRegistry
from app.framework.interfaces import BaseAgent
from app.agents.base_agent import BaseAgent as LegacyBaseAgent
from app.agents.schemas.agent_state import AgentState
from app.core.logging import logger

RISK_SYSTEM_PROMPT = """You are an expert B2B sales risk analyst.
Synthesize ALL available data and calculate comprehensive risk scores.

You have access to: CRM data, transcript analysis, email analysis, support analysis, and enterprise knowledge.

Return valid JSON:
{
    "overall_risk_score": 0.0-1.0,
    "risk_level": "low/medium/high/critical",
    "deal_risk": {"score": 0.0-1.0, "factors": ["reasons"], "mitigation": ["actions"]},
    "budget_risk": {"score": 0.0-1.0, "factors": ["reasons"], "mitigation": ["actions"]},
    "competitor_risk": {"score": 0.0-1.0, "factors": ["reasons"], "mitigation": ["actions"]},
    "delay_risk": {"score": 0.0-1.0, "factors": ["reasons"], "mitigation": ["actions"]},
    "churn_risk": {"score": 0.0-1.0, "factors": ["reasons"], "mitigation": ["actions"]},
    "explanation": "overall risk narrative",
    "top_risk_factors": ["ranked list of biggest risks"],
    "recommended_actions": ["immediate actions to reduce risk"]
}"""


@AgentRegistry.register("risk_agent")
class RiskAgent(BaseAgent, LegacyBaseAgent):
    """Calculates deal, budget, competitor, delay, and churn risk with explanations."""

    name = "risk_agent"
    description = "Calculates multi-dimensional deal risk"
    system_prompt = RISK_SYSTEM_PROMPT

    def __init__(self, *args, **kwargs):
        # Resolve multiple inheritance init
        LegacyBaseAgent.__init__(self)

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        customer = state.get("customer", {})
        transcript = state.get("transcript_analysis", {})
        email = state.get("email_analysis", {})
        support = state.get("support_analysis", {})
        docs = state.get("retrieved_documents", [])
        past_recs = state.get("past_recommendations", [])

        prompt = f"""Calculate risk scores for this customer:

CUSTOMER PROFILE:
{json.dumps(customer, indent=2, default=str)}

TRANSCRIPT ANALYSIS:
{json.dumps(transcript, indent=2, default=str)}

EMAIL ANALYSIS:
{json.dumps(email, indent=2, default=str)}

SUPPORT ANALYSIS:
{json.dumps(support, indent=2, default=str)}

RELEVANT KNOWLEDGE (top sources):
{json.dumps([d.get('content', '')[:500] for d in docs[:3]], indent=2)}

PAST RECOMMENDATIONS ({len(past_recs)} total):
{json.dumps(past_recs[:5], indent=2, default=str)}"""

        try:
            response = await self.invoke_llm(prompt)
            assessment = self.parse_json_response(response)
        except Exception as e:
            logger.warning(f"[risk_agent] LLM failed: {e}")
            assessment = self._heuristic_risk(customer, support)

        logger.info(
            f"[risk_agent] Risk: {assessment.get('risk_level', 'unknown')} "
            f"(score={assessment.get('overall_risk_score', 0)})"
        )

        return {**state, "risk_assessment": assessment}

    def _heuristic_risk(self, customer: dict, support: dict) -> dict:
        """Fallback heuristic when LLM is unavailable."""
        health = customer.get("health_score", 50)
        frustration = support.get("customer_frustration", {}).get("score", 0.3)
        score = round((1 - health / 100) * 0.5 + frustration * 0.5, 2)
        level = "low" if score < 0.3 else "medium" if score < 0.6 else "high" if score < 0.8 else "critical"
        return {
            "overall_risk_score": score,
            "risk_level": level,
            "deal_risk": {"score": score, "factors": ["heuristic calculation"], "mitigation": []},
            "budget_risk": {"score": 0.3, "factors": ["insufficient data"], "mitigation": []},
            "competitor_risk": {"score": 0.3, "factors": ["insufficient data"], "mitigation": []},
            "delay_risk": {"score": 0.3, "factors": ["insufficient data"], "mitigation": []},
            "churn_risk": {"score": frustration, "factors": ["support frustration"], "mitigation": []},
            "explanation": "Heuristic risk calculation (LLM unavailable)",
            "top_risk_factors": ["health_score_based"],
            "recommended_actions": ["Follow up with customer"],
        }
