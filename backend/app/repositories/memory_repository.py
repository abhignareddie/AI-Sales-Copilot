from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.memory import Memory


class MemoryRepository(BaseRepository[Memory]):
    def __init__(self, db: AsyncSession):
        super().__init__(Memory, db)

    async def get_by_customer(self, customer_id: int, skip: int = 0, limit: int = 20) -> tuple[list[Memory], int]:
        stmt = select(Memory).where(Memory.customer_id == customer_id)
        count_result = await self.db.execute(select(func.count()).select_from(stmt.subquery()))
        total = count_result.scalar() or 0
        stmt = stmt.order_by(Memory.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def get_by_type(self, memory_type: str, skip: int = 0, limit: int = 20) -> tuple[list[Memory], int]:
        stmt = select(Memory).where(Memory.memory_type == memory_type)
        count_result = await self.db.execute(select(func.count()).select_from(stmt.subquery()))
        total = count_result.scalar() or 0
        stmt = stmt.order_by(Memory.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total
