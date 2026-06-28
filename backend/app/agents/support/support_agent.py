"""Support Agent — Analyzes customer support tickets using LLM."""

from typing import Any
from app.framework.registry import AgentRegistry
from app.framework.interfaces import BaseAgent
from app.agents.base_agent import BaseAgent as LegacyBaseAgent
from app.agents.schemas.agent_state import AgentState
from app.core.logging import logger

SUPPORT_SYSTEM_PROMPT = """You are an expert customer support analyst.
Analyze the provided support tickets and calculate metrics.

Return valid JSON:
{
    "customer_frustration": {"score": 0.0-1.0, "level": "low/medium/high/critical", "reasons": ["why"]},
    "issue_frequency": {"total_tickets": 0, "open_tickets": 0, "critical_tickets": 0, "trend": "increasing/stable/decreasing"},
    "resolution_speed": {"average_status": "fast/normal/slow", "unresolved_count": 0},
    "open_issues": [{"ticket_number": "", "priority": "", "issue_summary": "", "days_open": 0}],
    "recurring_themes": ["common issue patterns"],
    "escalation_risk": "high/medium/low",
    "support_satisfaction": "good/fair/poor",
    "recommended_actions": ["actions to address support issues"]
}"""


@AgentRegistry.register("support_agent")
class SupportAgent(BaseAgent, LegacyBaseAgent):
    """Analyzes support tickets for frustration, patterns, and resolution metrics."""

    name = "support_agent"
    description = "Analyzes support ticket data"
    system_prompt = SUPPORT_SYSTEM_PROMPT

    def __init__(self, *args, **kwargs):
        LegacyBaseAgent.__init__(self)

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        tickets = state.get("support_tickets", [])

        if not tickets:
            logger.info("[support_agent] No support tickets available")
            return {
                **state,
                "support_analysis": {
                    "status": "no_tickets",
                    "customer_frustration": {"score": 0.0, "level": "low"},
                    "issue_frequency": {"total_tickets": 0, "open_tickets": 0},
                    "escalation_risk": "low",
                },
            }

        formatted = "\n\n".join(
            f"Ticket #{t['ticket_number']} | Priority: {t['priority']} | Status: {t['status']}\n"
            f"Issue: {t['issue'][:1000]}\n"
            f"Resolution: {t.get('resolution', 'Unresolved')}"
            for t in tickets[:15]
        )

        prompt = f"Analyze these {len(tickets)} support tickets:\n\n{formatted}"

        try:
            response = await self.invoke_llm(prompt)
            analysis = self.parse_json_response(response)
        except Exception as e:
            logger.warning(f"[support_agent] LLM failed: {e}")
            open_count = sum(1 for t in tickets if t.get("status") == "open")
            analysis = {
                "status": "llm_error",
                "customer_frustration": {"score": min(open_count / 5, 1.0), "level": "medium"},
                "issue_frequency": {"total_tickets": len(tickets), "open_tickets": open_count},
                "escalation_risk": "medium" if open_count > 2 else "low",
            }

        logger.info(
            f"[support_agent] Analyzed {len(tickets)} tickets: "
            f"frustration={analysis.get('customer_frustration', {}).get('level')}"
        )

        return {**state, "support_analysis": analysis}
