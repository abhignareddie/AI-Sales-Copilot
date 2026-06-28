"""Support Tool — Retrieves customer support tickets from the database."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.support_ticket import SupportTicket
from app.core.logging import logger


class SupportTool:
    """Retrieves support ticket data for agent analysis."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_customer_tickets(
        self, customer_id: int, limit: int = 20
    ) -> list[dict]:
        """Get recent support tickets for a customer."""
        result = await self.db.execute(
            select(SupportTicket)
            .where(SupportTicket.customer_id == customer_id)
            .order_by(SupportTicket.created_at.desc())
            .limit(limit)
        )
        tickets = result.scalars().all()
        logger.info(f"Retrieved {len(tickets)} tickets for customer {customer_id}")
        return [
            {
                "id": t.id,
                "ticket_number": t.ticket_number,
                "priority": t.priority,
                "status": t.status,
                "issue": t.issue,
                "resolution": t.resolution,
                "created_at": t.created_at.isoformat() if t.created_at else None,
            }
            for t in tickets
        ]
