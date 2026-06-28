from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, get_current_user
from app.schemas.email import EmailCreate, EmailUpdate, EmailResponse
from app.schemas.common import PaginatedResponse
from app.repositories.email_repository import EmailRepository
from app.services.audit_service import AuditService
from app.models.user import User

router = APIRouter()


@router.get("", response_model=PaginatedResponse[EmailResponse])
async def list_emails(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), customer_id: Optional[int] = None, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = EmailRepository(db)
    items, total = await repo.search_emails(customer_id=customer_id, skip=(page - 1) * page_size, limit=page_size)
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return {"items": items, "total": total, "page": page, "page_size": page_size, "total_pages": total_pages}


@router.get("/{email_id}", response_model=EmailResponse)
async def get_email(email_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = EmailRepository(db)
    email = await repo.get_by_id(email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return email


@router.post("", response_model=EmailResponse, status_code=201)
async def create_email(data: EmailCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = EmailRepository(db)
    audit = AuditService(db)
    email = await repo.create(data.model_dump())
    await audit.log("create", "email", email.id, current_user.id)
    from app.redis.client import invalidate_recommendation_cache
    await invalidate_recommendation_cache()
    return email


@router.put("/{email_id}", response_model=EmailResponse)
async def update_email(email_id: int, data: EmailUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = EmailRepository(db)
    audit = AuditService(db)
    email = await repo.update(email_id, data.model_dump(exclude_unset=True))
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    await audit.log("update", "email", email_id, current_user.id)
    from app.redis.client import invalidate_recommendation_cache
    await invalidate_recommendation_cache()
    return email


@router.delete("/{email_id}", status_code=204)
async def delete_email(email_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = EmailRepository(db)
    audit = AuditService(db)
    deleted = await repo.delete(email_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Email not found")
    await audit.log("delete", "email", email_id, current_user.id)
    from app.redis.client import invalidate_recommendation_cache
    await invalidate_recommendation_cache()
