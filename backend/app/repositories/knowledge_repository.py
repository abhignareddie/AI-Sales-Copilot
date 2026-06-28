from typing import Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.knowledge_document import KnowledgeDocument


class KnowledgeRepository(BaseRepository[KnowledgeDocument]):
    def __init__(self, db: AsyncSession):
        super().__init__(KnowledgeDocument, db)

    async def search_documents(
        self, query: str = "", document_type: Optional[str] = None, skip: int = 0, limit: int = 20,
    ) -> tuple[list[KnowledgeDocument], int]:
        stmt = select(KnowledgeDocument)
        filters = []
        if query:
            filters.append(KnowledgeDocument.title.ilike(f"%{query}%"))
        if document_type:
            filters.append(KnowledgeDocument.document_type == document_type)
        if filters:
            stmt = stmt.where(and_(*filters))
        count_result = await self.db.execute(select(func.count()).select_from(stmt.subquery()))
        total = count_result.scalar() or 0
        stmt = stmt.order_by(KnowledgeDocument.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total
