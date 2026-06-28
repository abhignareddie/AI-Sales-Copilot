from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, get_current_user
from app.repositories.customer_repository import CustomerRepository
from app.repositories.meeting_repository import MeetingRepository
from app.repositories.email_repository import EmailRepository
from app.repositories.knowledge_repository import KnowledgeRepository
from app.repositories.recommendation_repository import RecommendationRepository
from app.models.user import User

router = APIRouter()


@router.get("/global")
async def global_search(q: str = Query(..., min_length=1), limit: int = Query(5, ge=1, le=20), db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    customer_repo = CustomerRepository(db)
    meeting_repo = MeetingRepository(db)
    email_repo = EmailRepository(db)
    knowledge_repo = KnowledgeRepository(db)
    rec_repo = RecommendationRepository(db)
    customers, _ = await customer_repo.search_customers(query=q, limit=limit)
    meetings, _ = await meeting_repo.search_meetings(query=q, limit=limit)
    emails, _ = await email_repo.search_emails(query=q, limit=limit)
    documents, _ = await knowledge_repo.search_documents(query=q, limit=limit)
    recs, _ = await rec_repo.search_recommendations(query=q, limit=limit)
    return {
        "customers": [{"id": c.id, "company_name": c.company_name, "contact_person": c.contact_person, "email": c.email} for c in customers],
        "meetings": [{"id": m.id, "title": m.title, "meeting_date": m.meeting_date.isoformat() if m.meeting_date else None} for m in meetings],
        "emails": [{"id": e.id, "subject": e.subject, "sender": e.sender} for e in emails],
        "knowledge_documents": [{"id": d.id, "title": d.title, "document_type": d.document_type} for d in documents],
        "recommendations": [{"id": r.id, "recommendation": r.recommendation[:100], "status": r.status} for r in recs],
    }


@router.get("/customers")
async def search_customers(q: str = Query(""), industry: Optional[str] = None, current_stage: Optional[str] = None, min_revenue: Optional[float] = None, max_revenue: Optional[float] = None, min_health_score: Optional[float] = None, max_health_score: Optional[float] = None, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = CustomerRepository(db)
    items, total = await repo.search_customers(query=q, industry=industry, current_stage=current_stage, min_revenue=min_revenue, max_revenue=max_revenue, min_health_score=min_health_score, max_health_score=max_health_score, skip=(page - 1) * page_size, limit=page_size)
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return {"items": items, "total": total, "page": page, "page_size": page_size, "total_pages": total_pages}


@router.get("/meetings")
async def search_meetings(q: str = Query(""), customer_id: Optional[int] = None, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = MeetingRepository(db)
    items, total = await repo.search_meetings(query=q, customer_id=customer_id, skip=(page - 1) * page_size, limit=page_size)
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return {"items": items, "total": total, "page": page, "page_size": page_size, "total_pages": total_pages}


@router.get("/emails")
async def search_emails(q: str = Query(""), customer_id: Optional[int] = None, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = EmailRepository(db)
    items, total = await repo.search_emails(query=q, customer_id=customer_id, skip=(page - 1) * page_size, limit=page_size)
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return {"items": items, "total": total, "page": page, "page_size": page_size, "total_pages": total_pages}


@router.get("/knowledge")
async def search_knowledge(q: str = Query(""), document_type: Optional[str] = None, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = KnowledgeRepository(db)
    items, total = await repo.search_documents(query=q, document_type=document_type, skip=(page - 1) * page_size, limit=page_size)
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return {"items": items, "total": total, "page": page, "page_size": page_size, "total_pages": total_pages}


@router.get("/recommendations")
async def search_recommendations(q: str = Query(""), customer_id: Optional[int] = None, status: Optional[str] = None, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = RecommendationRepository(db)
    items, total = await repo.search_recommendations(query=q, customer_id=customer_id, status=status, skip=(page - 1) * page_size, limit=page_size)
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return {"items": items, "total": total, "page": page, "page_size": page_size, "total_pages": total_pages}
