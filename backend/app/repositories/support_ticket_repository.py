from typing import Optional
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.support_ticket import SupportTicket


class SupportTicketRepository(BaseRepository[SupportTicket]):
    def __init__(self, db: AsyncSession):
        super().__init__(SupportTicket, db)

    async def get_by_customer(self, customer_id: int, skip: int = 0, limit: int = 20) -> tuple[list[SupportTicket], int]:
        stmt = select(SupportTicket).where(SupportTicket.customer_id == customer_id)
        count_result = await self.db.execute(select(func.count()).select_from(stmt.subquery()))
        total = count_result.scalar() or 0
        stmt = stmt.order_by(SupportTicket.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def search_tickets(
        self, query: str = "", customer_id: Optional[int] = None,
        priority: Optional[str] = None, status: Optional[str] = None,
        skip: int = 0, limit: int = 20,
    ) -> tuple[list[SupportTicket], int]:
        stmt = select(SupportTicket)
        filters = []
        if query:
            filters.append(or_(SupportTicket.ticket_number.ilike(f"%{query}%"), SupportTicket.issue.ilike(f"%{query}%")))
        if customer_id:
            filters.append(SupportTicket.customer_id == customer_id)
        if priority:
            filters.append(SupportTicket.priority == priority)
        if status:
            filters.append(SupportTicket.status == status)
        if filters:
            stmt = stmt.where(and_(*filters))
        count_result = await self.db.execute(select(func.count()).select_from(stmt.subquery()))
        total = count_result.scalar() or 0
        stmt = stmt.order_by(SupportTicket.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def get_ticket_stats(self) -> dict:
        total = await self.db.execute(select(func.count(SupportTicket.id)))
        open_count = await self.db.execute(select(func.count(SupportTicket.id)).where(SupportTicket.status == "open"))
        result = await self.db.execute(
            select(SupportTicket.priority, func.count(SupportTicket.id).label("count")).group_by(SupportTicket.priority)
        )
        priority_dist = [{"priority": r.priority, "count": r.count} for r in result.all()]
        return {"total_tickets": total.scalar() or 0, "open_tickets": open_count.scalar() or 0, "priority_distribution": priority_dist}
