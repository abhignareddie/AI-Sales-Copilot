from typing import Optional
from datetime import datetime
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.meeting import Meeting


class MeetingRepository(BaseRepository[Meeting]):
    def __init__(self, db: AsyncSession):
        super().__init__(Meeting, db)

    async def get_by_customer(self, customer_id: int, skip: int = 0, limit: int = 20) -> tuple[list[Meeting], int]:
        stmt = select(Meeting).where(Meeting.customer_id == customer_id)
        count_result = await self.db.execute(select(func.count()).select_from(stmt.subquery()))
        total = count_result.scalar() or 0
        stmt = stmt.order_by(Meeting.meeting_date.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def search_meetings(
        self, query: str = "", customer_id: Optional[int] = None,
        date_from: Optional[datetime] = None, date_to: Optional[datetime] = None,
        skip: int = 0, limit: int = 20,
    ) -> tuple[list[Meeting], int]:
        stmt = select(Meeting)
        filters = []
        if query:
            filters.append(or_(Meeting.title.ilike(f"%{query}%"), Meeting.summary.ilike(f"%{query}%")))
        if customer_id:
            filters.append(Meeting.customer_id == customer_id)
        if date_from:
            filters.append(Meeting.meeting_date >= date_from)
        if date_to:
            filters.append(Meeting.meeting_date <= date_to)
        if filters:
            stmt = stmt.where(and_(*filters))
        count_result = await self.db.execute(select(func.count()).select_from(stmt.subquery()))
        total = count_result.scalar() or 0
        stmt = stmt.order_by(Meeting.meeting_date.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def get_meeting_stats(self) -> dict:
        total = await self.db.execute(select(func.count(Meeting.id)))
        return {"total_meetings": total.scalar() or 0}
