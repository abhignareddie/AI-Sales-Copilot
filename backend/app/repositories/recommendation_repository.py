from typing import Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.recommendation import Recommendation


class RecommendationRepository(BaseRepository[Recommendation]):
    def __init__(self, db: AsyncSession):
        super().__init__(Recommendation, db)

    async def get_by_customer(self, customer_id: int, skip: int = 0, limit: int = 20) -> tuple[list[Recommendation], int]:
        stmt = select(Recommendation).where(Recommendation.customer_id == customer_id)
        count_result = await self.db.execute(select(func.count()).select_from(stmt.subquery()))
        total = count_result.scalar() or 0
        stmt = stmt.order_by(Recommendation.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def search_recommendations(
        self, query: str = "", customer_id: Optional[int] = None, status: Optional[str] = None,
        skip: int = 0, limit: int = 20,
    ) -> tuple[list[Recommendation], int]:
        stmt = select(Recommendation)
        filters = []
        if query:
            filters.append(Recommendation.recommendation.ilike(f"%{query}%"))
        if customer_id:
            filters.append(Recommendation.customer_id == customer_id)
        if status:
            filters.append(Recommendation.status == status)
        if filters:
            stmt = stmt.where(and_(*filters))
        count_result = await self.db.execute(select(func.count()).select_from(stmt.subquery()))
        total = count_result.scalar() or 0
        stmt = stmt.order_by(Recommendation.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def get_recommendation_stats(self) -> dict:
        total = await self.db.execute(select(func.count(Recommendation.id)))
        pending = await self.db.execute(select(func.count(Recommendation.id)).where(Recommendation.status == "pending"))
        approved = await self.db.execute(select(func.count(Recommendation.id)).where(Recommendation.status == "approved"))
        implemented = await self.db.execute(select(func.count(Recommendation.id)).where(Recommendation.status == "implemented"))
        result = await self.db.execute(
            select(Recommendation.status, func.count(Recommendation.id).label("count")).group_by(Recommendation.status)
        )
        status_dist = [{"status": r.status, "count": r.count} for r in result.all()]
        return {"total": total.scalar() or 0, "pending": pending.scalar() or 0, "approved": approved.scalar() or 0, "implemented": implemented.scalar() or 0, "status_distribution": status_dist}
