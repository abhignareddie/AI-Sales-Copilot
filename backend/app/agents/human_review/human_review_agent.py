"""Human Review Agent — Prepares recommendations for human approval."""

from typing import Any
from app.framework.registry import AgentRegistry
from app.framework.interfaces import BaseAgent
from app.agents.base_agent import BaseAgent as LegacyBaseAgent
from app.agents.schemas.agent_state import AgentState
from app.core.logging import logger


@AgentRegistry.register("human_review_agent")
class HumanReviewAgent(BaseAgent):
    """
    Formats recommendations for human review.
    Recommendations do NOT auto-execute — they require explicit
    approve/reject/modify actions from a human reviewer.
    """

    name = "human_review_agent"
    description = "Prepares recommendations for human approval workflow"

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        recommendations = state.get("recommendations", [])
        customer = state.get("customer", {})
        risk = state.get("risk_assessment", {})
        opportunity = state.get("opportunity_assessment", {})
        confidence = state.get("confidence", 0.0)

        review_package = {
            "status": "pending_review",
            "customer_summary": {
                "company": customer.get("company_name", "Unknown"),
                "stage": customer.get("current_stage", "Unknown"),
                "health_score": customer.get("health_score", 0),
            },
            "risk_summary": {
                "level": risk.get("risk_level", "unknown"),
                "score": risk.get("overall_risk_score", 0),
                "top_factors": risk.get("top_risk_factors", [])[:3],
            },
            "opportunity_summary": {
                "win_probability": opportunity.get("win_probability", {}).get("score", 0),
                "overall": opportunity.get("overall_opportunity_score", 0),
            },
            "overall_confidence": confidence,
            "total_recommendations": len(recommendations),
            "recommendations": [
                {
                    "priority": rec.get("priority", i + 1),
                    "action": rec.get("action", ""),
                    "category": rec.get("category", "other"),
                    "confidence": rec.get("confidence", 0),
                    "expected_impact": rec.get("expected_impact", "medium"),
                    "reason": rec.get("reason", ""),
                    "evidence": rec.get("evidence", []),
                    "timeline": rec.get("timeline", "this_week"),
                    "review_status": "pending",
                    "reviewer_comment": None,
                }
                for i, rec in enumerate(recommendations)
            ],
            "review_actions": {
                "approve": "Accept recommendation as-is",
                "reject": "Reject recommendation with reason",
                "modify": "Accept with modifications",
                "comment": "Add feedback without changing status",
            },
        }

        logger.info(
            f"[human_review_agent] Prepared {len(recommendations)} recommendations "
            f"for human review"
        )

        return {**state, "human_review": review_package}
