from typing import Optional
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.customer import Customer


class CustomerRepository(BaseRepository[Customer]):
    def __init__(self, db: AsyncSession):
        super().__init__(Customer, db)

    async def search_customers(
        self, query: str = "", industry: Optional[str] = None,
        min_revenue: Optional[float] = None, max_revenue: Optional[float] = None,
        min_company_size: Optional[int] = None, max_company_size: Optional[int] = None,
        min_health_score: Optional[float] = None, max_health_score: Optional[float] = None,
        current_stage: Optional[str] = None, skip: int = 0, limit: int = 20,
    ) -> tuple[list[Customer], int]:
        stmt = select(Customer)
        filters = []
        if query:
            filters.append(or_(
                Customer.company_name.ilike(f"%{query}%"),
                Customer.contact_person.ilike(f"%{query}%"),
                Customer.email.ilike(f"%{query}%"),
            ))
        if industry:
            filters.append(Customer.industry == industry)
        if min_revenue is not None:
            filters.append(Customer.annual_revenue >= min_revenue)
        if max_revenue is not None:
            filters.append(Customer.annual_revenue <= max_revenue)
        if min_company_size is not None:
            filters.append(Customer.company_size >= min_company_size)
        if max_company_size is not None:
            filters.append(Customer.company_size <= max_company_size)
        if min_health_score is not None:
            filters.append(Customer.health_score >= min_health_score)
        if max_health_score is not None:
            filters.append(Customer.health_score <= max_health_score)
        if current_stage:
            filters.append(Customer.current_stage == current_stage)
        if filters:
            stmt = stmt.where(and_(*filters))
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0
        stmt = stmt.order_by(Customer.id.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def get_industry_distribution(self) -> list[dict]:
        result = await self.db.execute(
            select(Customer.industry, func.count(Customer.id).label("count")).group_by(Customer.industry)
        )
        return [{"industry": row.industry or "Unknown", "count": row.count} for row in result.all()]

    async def get_stage_distribution(self) -> list[dict]:
        result = await self.db.execute(
            select(Customer.current_stage, func.count(Customer.id).label("count")).group_by(Customer.current_stage)
        )
        return [{"stage": row.current_stage, "count": row.count} for row in result.all()]

    async def get_health_score_distribution(self) -> list[dict]:
        brackets = [
            {"label": "Critical (0-25)", "min": 0, "max": 25},
            {"label": "Low (25-50)", "min": 25, "max": 50},
            {"label": "Medium (50-75)", "min": 50, "max": 75},
            {"label": "High (75-100)", "min": 75, "max": 101},
        ]
        distribution = []
        for bracket in brackets:
            result = await self.db.execute(
                select(func.count(Customer.id)).where(
                    and_(Customer.health_score >= bracket["min"], Customer.health_score < bracket["max"])
                )
            )
            distribution.append({"label": bracket["label"], "count": result.scalar() or 0})
        return distribution

    async def get_revenue_distribution(self) -> list[dict]:
        brackets = [
            {"label": "< $100K", "min": 0, "max": 100000},
            {"label": "$100K - $500K", "min": 100000, "max": 500000},
            {"label": "$500K - $1M", "min": 500000, "max": 1000000},
            {"label": "$1M - $5M", "min": 1000000, "max": 5000000},
            {"label": "> $5M", "min": 5000000, "max": 999999999999},
        ]
        distribution = []
        for bracket in brackets:
            result = await self.db.execute(
                select(func.count(Customer.id)).where(
                    and_(Customer.annual_revenue >= bracket["min"], Customer.annual_revenue < bracket["max"])
                )
            )
            distribution.append({"label": bracket["label"], "count": result.scalar() or 0})
        return distribution
