from typing import TypeVar, Generic, Type, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self, skip: int = 0, limit: int = 20, order_by: str = "id", order_dir: str = "desc",
    ) -> tuple[list[ModelType], int]:
        count_query = select(func.count()).select_from(self.model)
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        query = select(self.model)
        order_column = getattr(self.model, order_by, self.model.id)
        if order_dir == "asc":
            query = query.order_by(order_column.asc())
        else:
            query = query.order_by(order_column.desc())

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        items = list(result.scalars().all())
        return items, total

    async def create(self, obj_data: dict) -> ModelType:
        db_obj = self.model(**obj_data)
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(self, id: int, obj_data: dict) -> Optional[ModelType]:
        db_obj = await self.get_by_id(id)
        if not db_obj:
            return None
        for key, value in obj_data.items():
            if value is not None:
                setattr(db_obj, key, value)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, id: int) -> bool:
        db_obj = await self.get_by_id(id)
        if not db_obj:
            return False
        await self.db.delete(db_obj)
        await self.db.flush()
        return True

    async def search(
        self, field: str, query: str, skip: int = 0, limit: int = 20
    ) -> tuple[list[ModelType], int]:
        column = getattr(self.model, field, None)
        if column is None:
            return [], 0
        search_query = select(self.model).where(column.ilike(f"%{query}%"))
        count_query = select(func.count()).select_from(search_query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        search_query = search_query.offset(skip).limit(limit)
        result = await self.db.execute(search_query)
        items = list(result.scalars().all())
        return items, total
