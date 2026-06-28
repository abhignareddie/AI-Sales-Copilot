"""Email Tool — Retrieves customer emails from the database."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.email import Email
from app.core.logging import logger


class EmailTool:
    """Retrieves email data for agent analysis."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_customer_emails(
        self, customer_id: int, limit: int = 20
    ) -> list[dict]:
        """Get recent emails for a customer."""
        result = await self.db.execute(
            select(Email)
            .where(Email.customer_id == customer_id)
            .order_by(Email.created_at.desc())
            .limit(limit)
        )
        emails = result.scalars().all()
        logger.info(f"Retrieved {len(emails)} emails for customer {customer_id}")
        return [
            {
                "id": e.id,
                "subject": e.subject,
                "sender": e.sender,
                "receiver": e.receiver,
                "body": e.body,
                "created_at": e.created_at.isoformat() if e.created_at else None,
            }
            for e in emails
        ]
