from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.audit_repository import AuditRepository
from app.models.audit_log import AuditLog
from app.core.logging import logger


class AuditService:
    def __init__(self, db: AsyncSession):
        self.repo = AuditRepository(db)

    async def log(self, action: str, entity: str, entity_id: Optional[int] = None, user_id: Optional[int] = None) -> AuditLog:
        logger.info(f"Audit: {action} {entity} {entity_id} by user {user_id}")
        return await self.repo.log_action(action, entity, entity_id, user_id)

    async def get_recent(self, limit: int = 20, user_id: Optional[int] = None, entity: Optional[str] = None, action: Optional[str] = None) -> list[AuditLog]:
        return await self.repo.get_recent_activities(limit, user_id, entity, action)

    async def get_all(self, skip: int = 0, limit: int = 20) -> tuple[list[AuditLog], int]:
        return await self.repo.get_all(skip, limit, order_by="timestamp")
