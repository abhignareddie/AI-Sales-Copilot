"""Transcript Agent — Analyzes meeting transcripts using LLM."""

from typing import Any
import json
from app.framework.registry import AgentRegistry
from app.framework.interfaces import BaseAgent
from app.agents.base_agent import BaseAgent as LegacyBaseAgent
from app.agents.schemas.agent_state import AgentState
from app.core.logging import logger

TRANSCRIPT_SYSTEM_PROMPT = """You are an expert sales conversation analyst.
Analyze the provided meeting transcripts and extract structured insights.

Return valid JSON:
{
    "pain_points": ["list of customer pain points"],
    "budget": {"mentioned": true/false, "range": "budget range if mentioned", "constraints": "any budget constraints"},
    "timeline": {"urgency": "high/medium/low", "deadline": "if mentioned", "notes": "timeline context"},
    "competitors": ["competitor names mentioned"],
    "decision_makers": [{"name": "person", "role": "their role", "influence": "high/medium/low"}],
    "sentiment": {"overall": "positive/neutral/negative", "score": 0.0-1.0, "notes": "sentiment details"},
    "action_items": ["list of follow-up actions"],
    "missing_information": ["information gaps that need to be filled"],
    "key_quotes": ["important direct quotes"],
    "engagement_level": "high/medium/low"
}"""


@AgentRegistry.register("transcript_agent")
class TranscriptAgent(BaseAgent, LegacyBaseAgent):
    """Analyzes meeting transcripts to extract actionable sales intelligence."""

    name = "transcript_agent"
    description = "Analyzes meeting transcripts for sales insights"
    system_prompt = TRANSCRIPT_SYSTEM_PROMPT

    def __init__(self, *args, **kwargs):
        LegacyBaseAgent.__init__(self)

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        meetings = state.get("meetings", [])
        transcripts = [m for m in meetings if m.get("transcript")]

        if not transcripts:
            logger.info("[transcript_agent] No transcripts available")
            return {
                **state,
                "transcript_analysis": {
                    "status": "no_transcripts",
                    "pain_points": [],
                    "sentiment": {"overall": "unknown", "score": 0.5},
                    "action_items": [],
                },
            }

        # Combine recent transcripts (limit to avoid token overflow)
        combined = "\n\n---\n\n".join(
            f"Meeting: {t['title']} ({t.get('meeting_date', 'N/A')})\n{t['transcript'][:3000]}"
            for t in transcripts[:5]
        )

        prompt = f"Analyze these meeting transcripts:\n\n{combined}"

        try:
            response = await self.invoke_llm(prompt)
            analysis = self.parse_json_response(response)
        except Exception as e:
            logger.warning(f"[transcript_agent] LLM failed: {e}")
            analysis = {
                "status": "llm_error",
                "error": str(e),
                "pain_points": [],
                "sentiment": {"overall": "unknown", "score": 0.5},
            }

        logger.info(
            f"[transcript_agent] Analyzed {len(transcripts)} transcripts: "
            f"{len(analysis.get('pain_points', []))} pain points found"
        )

        return {
            **state,
            "transcript_analysis": analysis,
        }
