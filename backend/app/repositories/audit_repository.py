from typing import Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.audit_log import AuditLog


class AuditRepository(BaseRepository[AuditLog]):
    def __init__(self, db: AsyncSession):
        super().__init__(AuditLog, db)

    async def log_action(self, action: str, entity: str, entity_id: Optional[int] = None, user_id: Optional[int] = None) -> AuditLog:
        return await self.create({"user_id": user_id, "action": action, "entity": entity, "entity_id": entity_id})

    async def get_recent_activities(self, limit: int = 20, user_id: Optional[int] = None, entity: Optional[str] = None, action: Optional[str] = None) -> list[AuditLog]:
        stmt = select(AuditLog)
        filters = []
        if user_id:
            filters.append(AuditLog.user_id == user_id)
        if entity:
            filters.append(AuditLog.entity == entity)
        if action:
            filters.append(AuditLog.action == action)
        if filters:
            stmt = stmt.where(and_(*filters))
        stmt = stmt.order_by(AuditLog.timestamp.desc()).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
