"""CRM Agent — Retrieves complete customer context from the database."""

from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.framework.registry import AgentRegistry
from app.framework.interfaces import BaseAgent
from app.agents.base_agent import BaseAgent as LegacyBaseAgent
from app.agents.schemas.agent_state import AgentState
from app.agents.tools.crm_tool import CRMTool
from app.core.logging import logger


@AgentRegistry.register("crm_agent")
class CRMAgent(BaseAgent):
    """
    Retrieves customer profile, meetings, emails, support tickets,
    and past recommendations from the CRM database.
    """

    name = "crm_agent"
    description = "Retrieves customer CRM data"

    def __init__(self, db: AsyncSession):
        self.crm_tool = CRMTool(db)

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:

        customer_id = state.get("customer_id", 0)
        context = await self.crm_tool.get_full_customer_context(customer_id)

        if "error" in context:
            logger.warning(f"[crm_agent] {context['error']}")
            return {**state, "agent_errors": {self.name: context["error"]}}

        logger.info(
            f"[crm_agent] Loaded customer '{context['customer'].get('company_name')}': "
            f"{len(context['meetings'])} meetings, {len(context['emails'])} emails, "
            f"{len(context['support_tickets'])} tickets"
        )

        return {
            **state,
            "customer": context["customer"],
            "meetings": context["meetings"],
            "emails": context["emails"],
            "support_tickets": context["support_tickets"],
            "past_recommendations": context["past_recommendations"],
        }
