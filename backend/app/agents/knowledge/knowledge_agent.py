"""Knowledge Agent — Retrieves enterprise documents from ChromaDB via RAG."""

from typing import Any
from app.framework.registry import AgentRegistry
from app.framework.interfaces import BaseAgent
from app.agents.base_agent import BaseAgent as LegacyBaseAgent
from app.agents.schemas.agent_state import AgentState
from app.agents.tools.knowledge_tool import KnowledgeTool
from app.core.logging import logger


@AgentRegistry.register("knowledge_agent")
class KnowledgeAgent(BaseAgent):
    """
    Searches enterprise knowledge base (sales playbooks, pricing,
    product docs, competitor guides) via ChromaDB RAG pipeline.
    """

    name = "knowledge_agent"
    description = "Retrieves relevant enterprise knowledge documents"

    def __init__(self):
        self.knowledge_tool = KnowledgeTool()

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        customer = state.get("customer", {})
        business_goal = state.get("business_goal", "")
        industry = customer.get("industry", "")
        stage = customer.get("current_stage", "")

        # Build contextual search query
        query = (
            f"{business_goal}. "
            f"Industry: {industry}. "
            f"Deal stage: {stage}. "
            f"Company: {customer.get('company_name', 'Unknown')}"
        )
        customer_context = (
            f"Revenue: {customer.get('annual_revenue', 'N/A')}, "
            f"Size: {customer.get('company_size', 'N/A')}, "
            f"Health: {customer.get('health_score', 'N/A')}"
        )

        try:
            documents = self.knowledge_tool.search_with_context(
                query=query,
                customer_context=customer_context,
                top_k=5,
            )
        except Exception as e:
            logger.warning(f"[knowledge_agent] ChromaDB search failed: {e}")
            documents = []

        logger.info(f"[knowledge_agent] Retrieved {len(documents)} knowledge chunks")

        return {
            **state,
            "retrieved_documents": documents,
        }
