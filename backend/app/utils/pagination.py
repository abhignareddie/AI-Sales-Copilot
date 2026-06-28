from typing import TypeVar, Generic
from pydantic import BaseModel
from sqlalchemy import select, func, Select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 20

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int

    class Config:
        from_attributes = True


async def paginate(
    db: AsyncSession, query: Select, page: int = 1, page_size: int = 20,
) -> dict:
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    paginated_query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(paginated_query)
    items = result.scalars().all()
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return {"items": items, "total": total, "page": page, "page_size": page_size, "total_pages": total_pages}
