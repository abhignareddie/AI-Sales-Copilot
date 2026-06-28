from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, get_current_user, require_role
from app.schemas.audit_log import AuditLogResponse
from app.schemas.common import PaginatedResponse
from app.services.audit_service import AuditService
from app.models.user import User

router = APIRouter()


@router.get("", response_model=PaginatedResponse[AuditLogResponse])
async def list_audit_logs(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: AsyncSession = Depends(get_db), current_user: User = Depends(require_role(["admin", "manager"]))):
    service = AuditService(db)
    items, total = await service.get_all(skip=(page - 1) * page_size, limit=page_size)
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return {"items": items, "total": total, "page": page, "page_size": page_size, "total_pages": total_pages}


@router.get("/recent", response_model=list[AuditLogResponse])
async def get_recent_activities(limit: int = Query(20, ge=1, le=100), user_id: Optional[int] = None, entity: Optional[str] = None, action: Optional[str] = None, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = AuditService(db)
    return await service.get_recent(limit=limit, user_id=user_id, entity=entity, action=action)
