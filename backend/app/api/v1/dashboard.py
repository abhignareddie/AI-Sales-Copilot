from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.dependencies import get_db, get_current_user
from app.models.customer import Customer
from app.models.meeting import Meeting
from app.models.support_ticket import SupportTicket
from app.models.recommendation import Recommendation
from app.repositories.customer_repository import CustomerRepository
from app.services.audit_service import AuditService
from app.models.user import User

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    total_customers = await db.execute(select(func.count(Customer.id)))
    active_deals = await db.execute(select(func.count(Customer.id)).where(Customer.current_stage.notin_(["closed_won", "closed_lost"])))
    pending_recs = await db.execute(select(func.count(Recommendation.id)).where(Recommendation.status == "pending"))
    completed_recs = await db.execute(select(func.count(Recommendation.id)).where(Recommendation.status == "implemented"))
    total_meetings = await db.execute(select(func.count(Meeting.id)))
    total_tickets = await db.execute(select(func.count(SupportTicket.id)))
    open_tickets = await db.execute(select(func.count(SupportTicket.id)).where(SupportTicket.status == "open"))
    total_revenue = await db.execute(select(func.coalesce(func.sum(Customer.annual_revenue), 0)))
    customer_repo = CustomerRepository(db)
    health_dist = await customer_repo.get_health_score_distribution()
    audit_service = AuditService(db)
    recent = await audit_service.get_recent(limit=10)
    return {
        "total_customers": total_customers.scalar() or 0,
        "active_deals": active_deals.scalar() or 0,
        "pending_recommendations": pending_recs.scalar() or 0,
        "completed_recommendations": completed_recs.scalar() or 0,
        "total_meetings": total_meetings.scalar() or 0,
        "total_tickets": total_tickets.scalar() or 0,
        "open_tickets": open_tickets.scalar() or 0,
        "total_revenue": total_revenue.scalar() or 0,
        "health_score_distribution": health_dist,
        "recent_activities": [{"id": a.id, "action": a.action, "entity": a.entity, "entity_id": a.entity_id, "timestamp": a.timestamp.isoformat() if a.timestamp else None} for a in recent],
    }
