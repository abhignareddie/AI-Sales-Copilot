from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, get_current_user
from app.schemas.support_ticket import SupportTicketCreate, SupportTicketUpdate, SupportTicketResponse
from app.schemas.common import PaginatedResponse
from app.repositories.support_ticket_repository import SupportTicketRepository
from app.services.audit_service import AuditService
from app.models.user import User

router = APIRouter()


@router.get("", response_model=PaginatedResponse[SupportTicketResponse])
async def list_tickets(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), customer_id: Optional[int] = None, priority: Optional[str] = None, status: Optional[str] = None, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = SupportTicketRepository(db)
    items, total = await repo.search_tickets(customer_id=customer_id, priority=priority, status=status, skip=(page - 1) * page_size, limit=page_size)
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return {"items": items, "total": total, "page": page, "page_size": page_size, "total_pages": total_pages}


@router.get("/{ticket_id}", response_model=SupportTicketResponse)
async def get_ticket(ticket_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = SupportTicketRepository(db)
    ticket = await repo.get_by_id(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.post("", response_model=SupportTicketResponse, status_code=201)
async def create_ticket(data: SupportTicketCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = SupportTicketRepository(db)
    audit = AuditService(db)
    ticket = await repo.create(data.model_dump())
    await audit.log("create", "support_ticket", ticket.id, current_user.id)
    from app.redis.client import invalidate_recommendation_cache
    await invalidate_recommendation_cache()
    return ticket


@router.put("/{ticket_id}", response_model=SupportTicketResponse)
async def update_ticket(ticket_id: int, data: SupportTicketUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = SupportTicketRepository(db)
    audit = AuditService(db)
    ticket = await repo.update(ticket_id, data.model_dump(exclude_unset=True))
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    await audit.log("update", "support_ticket", ticket_id, current_user.id)
    from app.redis.client import invalidate_recommendation_cache
    await invalidate_recommendation_cache()
    return ticket


@router.delete("/{ticket_id}", status_code=204)
async def delete_ticket(ticket_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = SupportTicketRepository(db)
    audit = AuditService(db)
    deleted = await repo.delete(ticket_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Ticket not found")
    await audit.log("delete", "support_ticket", ticket_id, current_user.id)
    from app.redis.client import invalidate_recommendation_cache
    await invalidate_recommendation_cache()
