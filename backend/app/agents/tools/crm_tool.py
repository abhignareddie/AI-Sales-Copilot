"""CRM Tool — Retrieves customer data from the database."""

from __future__ import annotations

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.customer import Customer
from app.models.meeting import Meeting
from app.models.email import Email
from app.models.support_ticket import SupportTicket
from app.models.recommendation import Recommendation
from app.core.logging import logger


class CRMTool:
    """Retrieves CRM data for a customer from PostgreSQL."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_customer_profile(self, customer_id: int) -> dict:
        """Get full customer profile with all related data."""
        result = await self.db.execute(
            select(Customer).where(Customer.id == customer_id)
        )
        customer = result.scalar_one_or_none()
        if not customer:
            logger.warning(f"Customer {customer_id} not found")
            return {}

        return {
            "id": customer.id,
            "company_name": customer.company_name,
            "contact_person": customer.contact_person,
            "email": customer.email,
            "phone": customer.phone,
            "industry": customer.industry,
            "annual_revenue": customer.annual_revenue,
            "company_size": customer.company_size,
            "current_stage": customer.current_stage,
            "health_score": customer.health_score,
            "created_at": customer.created_at.isoformat() if customer.created_at else None,
        }

    async def get_customer_meetings(self, customer_id: int) -> list[dict]:
        """Get all meetings for a customer."""
        result = await self.db.execute(
            select(Meeting)
            .where(Meeting.customer_id == customer_id)
            .order_by(Meeting.meeting_date.desc())
        )
        meetings = result.scalars().all()
        return [
            {
                "id": m.id,
                "title": m.title,
                "transcript": m.transcript,
                "meeting_date": m.meeting_date.isoformat() if m.meeting_date else None,
                "summary": m.summary,
            }
            for m in meetings
        ]

    async def get_customer_emails(self, customer_id: int) -> list[dict]:
        """Get all emails for a customer."""
        result = await self.db.execute(
            select(Email)
            .where(Email.customer_id == customer_id)
            .order_by(Email.created_at.desc())
        )
        emails = result.scalars().all()
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

    async def get_customer_tickets(self, customer_id: int) -> list[dict]:
        """Get all support tickets for a customer."""
        result = await self.db.execute(
            select(SupportTicket)
            .where(SupportTicket.customer_id == customer_id)
            .order_by(SupportTicket.created_at.desc())
        )
        tickets = result.scalars().all()
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

    async def get_past_recommendations(self, customer_id: int) -> list[dict]:
        """Get past recommendations for a customer."""
        result = await self.db.execute(
            select(Recommendation)
            .where(Recommendation.customer_id == customer_id)
            .order_by(Recommendation.created_at.desc())
            .limit(20)
        )
        recs = result.scalars().all()
        return [
            {
                "id": r.id,
                "recommendation": r.recommendation,
                "confidence": r.confidence,
                "status": r.status,
                "evidence": r.evidence,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in recs
        ]

    async def get_full_customer_context(self, customer_id: int) -> dict:
        """Get complete customer context for agent pipeline."""
        profile = await self.get_customer_profile(customer_id)
        if not profile:
            return {"error": f"Customer {customer_id} not found"}

        meetings = await self.get_customer_meetings(customer_id)
        emails = await self.get_customer_emails(customer_id)
        tickets = await self.get_customer_tickets(customer_id)
        past_recs = await self.get_past_recommendations(customer_id)

        return {
            "customer": profile,
            "meetings": meetings,
            "emails": emails,
            "support_tickets": tickets,
            "past_recommendations": past_recs,
        }
