"""Email Agent — Analyzes customer email communications using LLM."""

from typing import Any
from app.framework.registry import AgentRegistry
from app.framework.interfaces import BaseAgent
from app.agents.base_agent import BaseAgent as LegacyBaseAgent
from app.agents.schemas.agent_state import AgentState
from app.core.logging import logger

EMAIL_SYSTEM_PROMPT = """You are an expert email communication analyst for enterprise sales.
Analyze the provided email thread and extract structured insights.

Return valid JSON:
{
    "intent": "primary intent of the email thread (inquiry/complaint/follow-up/negotiation/feedback)",
    "urgency": "high/medium/low",
    "customer_mood": "enthusiastic/positive/neutral/concerned/frustrated/angry",
    "mood_score": 0.0-1.0,
    "follow_up_requests": ["explicit follow-up requests from the customer"],
    "commitments": ["commitments made by either party"],
    "key_topics": ["main topics discussed"],
    "unanswered_questions": ["questions that remain unanswered"],
    "relationship_signals": "positive/neutral/negative indicators about the relationship",
    "recommended_response_urgency": "immediate/within_24h/within_week/no_rush"
}"""


@AgentRegistry.register("email_agent")
class EmailAgent(BaseAgent, LegacyBaseAgent):
    """Analyzes customer email communications for intent, urgency, and mood."""

    name = "email_agent"
    description = "Analyzes email communications for sales insights"
    system_prompt = EMAIL_SYSTEM_PROMPT

    def __init__(self, *args, **kwargs):
        LegacyBaseAgent.__init__(self)

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        emails = state.get("emails", [])

        if not emails:
            logger.info("[email_agent] No emails available")
            return {
                **state,
                "email_analysis": {
                    "status": "no_emails",
                    "intent": "unknown",
                    "urgency": "low",
                    "customer_mood": "neutral",
                },
            }

        # Format emails for analysis (limit to recent)
        formatted = "\n\n---\n\n".join(
            f"From: {e['sender']} → To: {e['receiver']}\n"
            f"Subject: {e['subject']}\n"
            f"Date: {e.get('created_at', 'N/A')}\n"
            f"Body: {(e.get('body') or '')[:2000]}"
            for e in emails[:10]
        )

        prompt = f"Analyze this email thread:\n\n{formatted}"

        try:
            response = await self.invoke_llm(prompt)
            analysis = self.parse_json_response(response)
        except Exception as e:
            logger.warning(f"[email_agent] LLM failed: {e}")
            analysis = {
                "status": "llm_error",
                "error": str(e),
                "intent": "unknown",
                "urgency": "medium",
                "customer_mood": "neutral",
            }

        logger.info(
            f"[email_agent] Analyzed {len(emails)} emails: "
            f"intent={analysis.get('intent')}, urgency={analysis.get('urgency')}"
        )

        return {**state, "email_analysis": analysis}
