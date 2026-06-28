from typing import Optional
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.email import Email


class EmailRepository(BaseRepository[Email]):
    def __init__(self, db: AsyncSession):
        super().__init__(Email, db)

    async def get_by_customer(self, customer_id: int, skip: int = 0, limit: int = 20) -> tuple[list[Email], int]:
        stmt = select(Email).where(Email.customer_id == customer_id)
        count_result = await self.db.execute(select(func.count()).select_from(stmt.subquery()))
        total = count_result.scalar() or 0
        stmt = stmt.order_by(Email.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def search_emails(
        self, query: str = "", customer_id: Optional[int] = None, skip: int = 0, limit: int = 20,
    ) -> tuple[list[Email], int]:
        stmt = select(Email)
        filters = []
        if query:
            filters.append(or_(Email.subject.ilike(f"%{query}%"), Email.sender.ilike(f"%{query}%"), Email.receiver.ilike(f"%{query}%")))
        if customer_id:
            filters.append(Email.customer_id == customer_id)
        if filters:
            stmt = stmt.where(and_(*filters))
        count_result = await self.db.execute(select(func.count()).select_from(stmt.subquery()))
        total = count_result.scalar() or 0
        stmt = stmt.order_by(Email.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total
