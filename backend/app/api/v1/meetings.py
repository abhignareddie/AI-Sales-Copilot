from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, get_current_user
from app.schemas.meeting import MeetingCreate, MeetingUpdate, MeetingResponse
from app.schemas.common import PaginatedResponse
from app.repositories.meeting_repository import MeetingRepository
from app.services.audit_service import AuditService
from app.models.user import User

router = APIRouter()


@router.get("", response_model=PaginatedResponse[MeetingResponse])
async def list_meetings(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    customer_id: Optional[int] = None, date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user),
):
    repo = MeetingRepository(db)
    items, total = await repo.search_meetings(customer_id=customer_id, date_from=date_from, date_to=date_to, skip=(page - 1) * page_size, limit=page_size)
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return {"items": items, "total": total, "page": page, "page_size": page_size, "total_pages": total_pages}


@router.get("/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(meeting_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = MeetingRepository(db)
    meeting = await repo.get_by_id(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting


@router.post("", response_model=MeetingResponse, status_code=201)
async def create_meeting(data: MeetingCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = MeetingRepository(db)
    audit = AuditService(db)
    meeting = await repo.create(data.model_dump())
    await audit.log("create", "meeting", meeting.id, current_user.id)
    from app.redis.client import invalidate_recommendation_cache
    await invalidate_recommendation_cache()
    return meeting


@router.put("/{meeting_id}", response_model=MeetingResponse)
async def update_meeting(meeting_id: int, data: MeetingUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = MeetingRepository(db)
    audit = AuditService(db)
    meeting = await repo.update(meeting_id, data.model_dump(exclude_unset=True))
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    await audit.log("update", "meeting", meeting_id, current_user.id)
    from app.redis.client import invalidate_recommendation_cache
    await invalidate_recommendation_cache()
    return meeting


@router.delete("/{meeting_id}", status_code=204)
async def delete_meeting(meeting_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = MeetingRepository(db)
    audit = AuditService(db)
    deleted = await repo.delete(meeting_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Meeting not found")
    await audit.log("delete", "meeting", meeting_id, current_user.id)
    from app.redis.client import invalidate_recommendation_cache
    await invalidate_recommendation_cache()
