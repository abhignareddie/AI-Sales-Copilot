"""Planner Agent — Dynamically decides which agents to execute and in what order."""

from typing import Any

from app.agents.llm_provider import get_llm
from app.framework.registry import AgentRegistry
from app.framework.interfaces import BaseAgent
from app.agents.base_agent import BaseAgent as LegacyBaseAgent
from app.agents.schemas.agent_state import AgentState
from app.core.logging import logger


PLANNER_SYSTEM_PROMPT = """You are an AI Sales Copilot Planner. You analyze the input and decide which specialized agents should execute.

Available agents:
1. crm_agent — Retrieves customer CRM data (profile, deals, history)
2. knowledge_agent — Searches enterprise knowledge base (playbooks, pricing, docs)
3. transcript_agent — Analyzes meeting transcripts for insights
4. email_agent — Analyzes email communications
5. support_agent — Analyzes support tickets
6. risk_agent — Calculates deal and churn risks
7. opportunity_agent — Estimates win probability and upsell/cross-sell
8. recommendation_agent — Generates top-5 next best actions
9. human_review_agent — Prepares recommendations for human approval
10. memory_agent — Stores and retrieves long-term customer memory

Rules:
- crm_agent ALWAYS runs first
- risk_agent and opportunity_agent need CRM + analysis data
- recommendation_agent needs risk + opportunity assessments
- human_review_agent always runs after recommendation_agent
- memory_agent always runs last
- Agents 2-5 can run in parallel
- Include reasoning for each decision

Return valid JSON with this exact structure:
{
    "agents_to_call": ["list of agent names to execute"],
    "execution_order": [
        {"step": 1, "agents": ["crm_agent"], "parallel": false},
        {"step": 2, "agents": ["knowledge_agent", "transcript_agent", "email_agent", "support_agent"], "parallel": true},
        {"step": 3, "agents": ["risk_agent"], "parallel": false},
        {"step": 4, "agents": ["opportunity_agent"], "parallel": false},
        {"step": 5, "agents": ["recommendation_agent"], "parallel": false},
        {"step": 6, "agents": ["human_review_agent"], "parallel": false},
        {"step": 7, "agents": ["memory_agent"], "parallel": false}
    ],
    "reasoning": "explanation of the plan",
    "parallel_opportunities": ["list of agents that can run concurrently"],
    "skipped_agents": ["agents not needed and why"]
}"""


@AgentRegistry.register("planner_agent")
class PlannerAgent(BaseAgent, LegacyBaseAgent):
    """
    Orchestration brain. Examines input, memory, and business goal,
    then dynamically determines which agents to call and in what order.
    """

    name = "planner_agent"
    description = "Plans and orchestrates the multi-agent pipeline"
    system_prompt = PLANNER_SYSTEM_PROMPT

    def __init__(self, *args, **kwargs):
        LegacyBaseAgent.__init__(self)
        self.llm = get_llm()

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        customer_id = state.get("customer_id", 0)
        business_goal = state.get(
            "business_goal",
            "Generate next best actions"
        )
        memory = state.get("memory", [])

        prompt = f"""Plan the agent execution for:

Customer ID: {customer_id}
Business Goal: {business_goal}
Available Memory: {len(memory)} records loaded
Memory Summary: {self._summarize_memory(memory)}

Determine which agents should execute and the optimal execution order.
Consider what data is available and what analysis is needed."""

        try:
            response = await self.invoke_llm(prompt)
            decisions = self.parse_json_response(response)
        except Exception as e:
            logger.warning(
                f"[planner] LLM call failed, using default plan: {e}"
            )
            decisions = self._default_plan()

        decisions = self._validate_plan(decisions)

        logger.info(
            f"[planner] Plan: "
            f"{len(decisions.get('agents_to_call', []))} agents, "
            f"reasoning: "
            f"{decisions.get('reasoning', 'N/A')[:100]}"
        )

        return {
            **state,
            "planner_decisions": decisions,
        }

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """
        Public entry point expected by tests.
        """
        result = await self.execute(state)

        executed = result.get("executed_agents", [])
        if "planner_agent" not in executed:
            executed.append("planner_agent")

        result["executed_agents"] = executed
        return result

    def _summarize_memory(self, memory: list[dict]) -> str:
        if not memory:
            return "No previous memory"

        types = {
            m.get("memory_type", "")
            for m in memory
            if m.get("memory_type")
        }

        return f"Types: {', '.join(types)}, Count: {len(memory)}"

    def summarize_memory(self, memory: list[dict]) -> str:
        return self._summarize_memory(memory)

    def _default_plan(self) -> dict:
        """
        Fallback plan when LLM is unavailable.
        """
        return {
            "agents_to_call": [
                "crm_agent",
                "knowledge_agent",
                "transcript_agent",
                "email_agent",
                "support_agent",
                "risk_agent",
                "opportunity_agent",
                "recommendation_agent",
                "human_review_agent",
                "memory_agent",
            ],
            "execution_order": [
                {
                    "step": 1,
                    "agents": ["crm_agent"],
                    "parallel": False,
                },
                {
                    "step": 2,
                    "agents": [
                        "knowledge_agent",
                        "transcript_agent",
                        "email_agent",
                        "support_agent",
                    ],
                    "parallel": True,
                },
                {
                    "step": 3,
                    "agents": ["risk_agent"],
                    "parallel": False,
                },
                {
                    "step": 4,
                    "agents": ["opportunity_agent"],
                    "parallel": False,
                },
                {
                    "step": 5,
                    "agents": ["recommendation_agent"],
                    "parallel": False,
                },
                {
                    "step": 6,
                    "agents": ["human_review_agent"],
                    "parallel": False,
                },
                {
                    "step": 7,
                    "agents": ["memory_agent"],
                    "parallel": False,
                },
            ],
            "reasoning": (
                "Default execution plan (LLM unavailable). "
                "Running all agents."
            ),
            "parallel_opportunities": [
                "knowledge_agent",
                "transcript_agent",
                "email_agent",
                "support_agent",
            ],
            "skipped_agents": [],
        }

    def default_plan(self) -> dict:
        return self._default_plan()

    def _validate_plan(self, decisions: dict) -> dict:
        """
        Ensure required agents are always included.
        """
        required = {
            "crm_agent",
            "recommendation_agent",
            "human_review_agent",
            "memory_agent",
        }

        agents = set(decisions.get("agents_to_call", []))
        agents.update(required)

        decisions["agents_to_call"] = list(agents)

        if not decisions.get("execution_order"):
            decisions["execution_order"] = (
                self._default_plan()["execution_order"]
            )

        return decisions

    def validate_plan(self, decisions: dict) -> dict:
        return self._validate_plan(decisions)