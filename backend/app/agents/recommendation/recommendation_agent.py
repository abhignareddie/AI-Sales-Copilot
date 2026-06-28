"""Recommendation Agent — Generates top-5 Next Best Actions with explainability."""

from typing import Any
import json
from app.framework.registry import AgentRegistry
from app.framework.interfaces import BaseAgent
from app.agents.base_agent import BaseAgent as LegacyBaseAgent
from app.agents.schemas.agent_state import AgentState
from app.core.logging import logger

RECOMMENDATION_SYSTEM_PROMPT = """You are an expert B2B sales strategist generating Next Best Actions.

Synthesize ALL available data: CRM profile, risk assessment, opportunity assessment,
transcript analysis, email analysis, support analysis, knowledge documents, and memory.

Generate exactly 5 recommendations. Each MUST include explainability.

Return valid JSON:
{
    "recommendations": [
        {
            "priority": 1,
            "action": "specific actionable recommendation",
            "category": "follow_up/pricing/demo/escalation/content/meeting/proposal/other",
            "reason": "detailed explanation of why this action",
            "evidence": ["specific data points supporting this"],
            "confidence": 0.0-1.0,
            "expected_impact": "high/medium/low",
            "supporting_crm_data": "relevant CRM data that supports this",
            "supporting_knowledge": "relevant knowledge base info",
            "supporting_meetings": "relevant meeting insights",
            "supporting_emails": "relevant email insights",
            "why_this_recommendation": "detailed reasoning for choosing this",
            "why_alternatives_rejected": "why other approaches were not chosen",
            "timeline": "when to execute (immediate/this_week/this_month)"
        }
    ],
    "overall_confidence": 0.0-1.0,
    "overall_strategy": "brief description of the recommended overall approach",
    "evidence_summary": ["top evidence points across all recommendations"]
}"""


@AgentRegistry.register("recommendation_agent")
class RecommendationAgent(BaseAgent, LegacyBaseAgent):
    """Generates top-5 Next Best Actions with full explainability chain."""

    name = "recommendation_agent"
    description = "Generates explainable next best action recommendations"
    system_prompt = RECOMMENDATION_SYSTEM_PROMPT

    def __init__(self, *args, **kwargs):
        LegacyBaseAgent.__init__(self)

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        customer = state.get("customer", {})
        risk = state.get("risk_assessment", {})
        opportunity = state.get("opportunity_assessment", {})
        transcript = state.get("transcript_analysis", {})
        email_analysis = state.get("email_analysis", {})
        support = state.get("support_analysis", {})
        docs = state.get("retrieved_documents", [])
        memory = state.get("memory", [])
        business_goal = state.get("business_goal", "")
        past_recs = state.get("past_recommendations", [])

        prompt = f"""Generate top-5 Next Best Actions for this customer.

BUSINESS GOAL: {business_goal}

CUSTOMER PROFILE:
{json.dumps(customer, indent=2, default=str)}

RISK ASSESSMENT:
Overall risk: {risk.get('risk_level', 'unknown')} (score: {risk.get('overall_risk_score', 'N/A')})
Top risks: {json.dumps(risk.get('top_risk_factors', []))}

OPPORTUNITY ASSESSMENT:
Win probability: {opportunity.get('win_probability', {}).get('score', 'N/A')}
Upsell: {opportunity.get('upsell_opportunity', {}).get('score', 'N/A')}
Cross-sell: {opportunity.get('cross_sell_opportunity', {}).get('score', 'N/A')}

TRANSCRIPT INSIGHTS:
Pain points: {json.dumps(transcript.get('pain_points', []))}
Sentiment: {transcript.get('sentiment', {}).get('overall', 'unknown')}
Action items: {json.dumps(transcript.get('action_items', []))}

EMAIL INSIGHTS:
Intent: {email_analysis.get('intent', 'unknown')}
Urgency: {email_analysis.get('urgency', 'unknown')}
Mood: {email_analysis.get('customer_mood', 'unknown')}

SUPPORT INSIGHTS:
Frustration: {support.get('customer_frustration', {}).get('level', 'unknown')}
Open issues: {support.get('issue_frequency', {}).get('open_tickets', 0)}

KNOWLEDGE BASE CONTEXT:
{json.dumps([d.get('content', '')[:400] for d in docs[:3]], indent=2)}

CUSTOMER MEMORY ({len(memory)} records):
{json.dumps(memory[:5], indent=2, default=str)}

PAST RECOMMENDATIONS ({len(past_recs)} total):
{json.dumps([{{'action': r.get('recommendation', '')[:100], 'status': r.get('status')}} for r in past_recs[:5]], indent=2, default=str)}

Generate 5 prioritized, actionable recommendations with full evidence chains."""

        try:
            response = await self.invoke_llm(prompt)
            result = self.parse_json_response(response)
        except Exception as e:
            logger.warning(f"[recommendation_agent] LLM failed: {e}")
            result = self._fallback_recommendations(customer, risk, opportunity)

        recommendations = result.get("recommendations", [])
        confidence = result.get("overall_confidence", 0.5)
        evidence = result.get("evidence_summary", [])

        logger.info(
            f"[recommendation_agent] Generated {len(recommendations)} recommendations "
            f"(confidence={confidence})"
        )

        return {
            **state,
            "recommendations": recommendations,
            "confidence": confidence,
            "evidence": evidence,
        }

    def _fallback_recommendations(self, customer: dict, risk: dict, opportunity: dict) -> dict:
        """Fallback recommendations when LLM is unavailable."""
        stage = customer.get("current_stage", "prospect")
        risk_level = risk.get("risk_level", "medium")
        recs = []

        if risk_level in ("high", "critical"):
            recs.append({
                "priority": 1, "action": "Schedule urgent customer check-in call",
                "category": "escalation", "reason": f"High risk level detected: {risk_level}",
                "evidence": ["risk assessment"], "confidence": 0.7,
                "expected_impact": "high", "timeline": "immediate",
                "why_this_recommendation": "Risk mitigation is the top priority",
                "why_alternatives_rejected": "Cannot proceed with growth actions under high risk",
            })

        recs.append({
            "priority": len(recs) + 1, "action": f"Review and update deal strategy for {stage} stage",
            "category": "follow_up", "reason": f"Customer is in {stage} stage",
            "evidence": ["CRM stage data"], "confidence": 0.6,
            "expected_impact": "medium", "timeline": "this_week",
            "why_this_recommendation": "Stage-appropriate engagement",
            "why_alternatives_rejected": "Generic recommendation due to LLM unavailability",
        })

        while len(recs) < 5:
            recs.append({
                "priority": len(recs) + 1, "action": "Gather more customer data for better analysis",
                "category": "other", "reason": "Insufficient data for detailed recommendation",
                "evidence": ["limited data"], "confidence": 0.3,
                "expected_impact": "low", "timeline": "this_week",
                "why_this_recommendation": "More data improves recommendation quality",
                "why_alternatives_rejected": "N/A",
            })

        return {
            "recommendations": recs[:5],
            "overall_confidence": 0.4,
            "overall_strategy": "Fallback strategy — gather more data and mitigate risks",
            "evidence_summary": ["Heuristic-based recommendations (LLM unavailable)"],
        }
