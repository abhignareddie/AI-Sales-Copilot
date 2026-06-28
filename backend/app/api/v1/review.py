from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.recommendation import Recommendation, RecommendationStatus
from app.models.comment import Comment
from app.models.audit_log_entry import AuditLogEntry
from app.services.hitl_service import ApprovalWorkflowEngine, NotificationService
from app.schemas.recommendation import RecommendationResponse, ActionRequest, ModifyRequest
from app.schemas.common import PaginatedResponse

router = APIRouter()

class EscalateRequest(BaseModel):
    recommendation_id: int
    reviewer_id: int
    comments: Optional[str] = None

class CommentCreateRequest(BaseModel):
    recommendation_id: int
    content: str
    parent_id: Optional[int] = None

class CommentResponse(BaseModel):
    id: int
    recommendation_id: int
    user_id: int
    content: str
    parent_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ReviewAnalytics(BaseModel):
    approval_rate: float
    average_review_time_hours: float
    accuracy_rate: float
    escalation_count: int

# POST /review/approve
@router.post("/approve", response_model=RecommendationResponse)
async def approve_recommendation(
    req: ActionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rec = await db.get(Recommendation, req.recommendation_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
        
    before_state = {"status": rec.status}
    
    rec.status = RecommendationStatus.APPROVED
    rec.reviewer_id = current_user.id
    rec.reviewed_at = datetime.now(timezone.utc)
    rec.comments = req.comments
    
    # Save audit log
    audit = AuditLogEntry(
        user_id=current_user.id,
        action="approve",
        entity="recommendation",
        entity_id=rec.id,
        before_state=before_state,
        after_state={"status": rec.status}
    )
    db.add(audit)
    await db.commit()
    await db.refresh(rec)
    
    await NotificationService.notify(
        event="approved",
        message=f"Recommendation #{rec.id} has been approved by {current_user.full_name}",
        user_id=rec.customer_id
    )
    return rec

# POST /review/reject
@router.post("/reject", response_model=RecommendationResponse)
async def reject_recommendation(
    req: ActionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rec = await db.get(Recommendation, req.recommendation_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
        
    before_state = {"status": rec.status}
    
    rec.status = RecommendationStatus.REJECTED
    rec.reviewer_id = current_user.id
    rec.reviewed_at = datetime.now(timezone.utc)
    rec.comments = req.comments
    
    audit = AuditLogEntry(
        user_id=current_user.id,
        action="reject",
        entity="recommendation",
        entity_id=rec.id,
        before_state=before_state,
        after_state={"status": rec.status}
    )
    db.add(audit)
    await db.commit()
    await db.refresh(rec)
    
    await NotificationService.notify(
        event="rejected",
        message=f"Recommendation #{rec.id} was rejected by {current_user.full_name}",
        user_id=rec.customer_id
    )
    return rec

# POST /review/modify
@router.post("/modify", response_model=RecommendationResponse)
async def modify_recommendation(
    req: ModifyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rec = await db.get(Recommendation, req.recommendation_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
        
    before_state = {"status": rec.status, "recommendation": rec.recommendation}
    
    rec.recommendation = req.recommendation
    rec.status = RecommendationStatus.APPROVED # Modified results in approval
    rec.reviewer_id = current_user.id
    rec.reviewed_at = datetime.now(timezone.utc)
    rec.comments = req.comments
    
    audit = AuditLogEntry(
        user_id=current_user.id,
        action="modify",
        entity="recommendation",
        entity_id=rec.id,
        before_state=before_state,
        after_state={"status": rec.status, "recommendation": rec.recommendation}
    )
    db.add(audit)
    await db.commit()
    await db.refresh(rec)
    
    return rec

# POST /review/escalate
@router.post("/escalate", response_model=RecommendationResponse)
async def escalate_recommendation(
    req: EscalateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rec = await db.get(Recommendation, req.recommendation_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
        
    before_state = {"status": rec.status, "reviewer_id": rec.reviewer_id}
    
    rec.status = RecommendationStatus.ESCALATED
    rec.reviewer_id = req.reviewer_id
    rec.comments = req.comments
    
    audit = AuditLogEntry(
        user_id=current_user.id,
        action="escalate",
        entity="recommendation",
        entity_id=rec.id,
        before_state=before_state,
        after_state={"status": rec.status, "reviewer_id": rec.reviewer_id}
    )
    db.add(audit)
    await db.commit()
    await db.refresh(rec)
    
    await NotificationService.notify(
        event="escalation",
        message=f"Recommendation #{rec.id} escalated to user {req.reviewer_id}",
        user_id=req.reviewer_id
    )
    return rec

# POST /review/comment
@router.post("/comment", response_model=CommentResponse)
async def post_comment(
    req: CommentCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Validate recommendation exists
    rec = await db.get(Recommendation, req.recommendation_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
        
    comment = Comment(
        recommendation_id=req.recommendation_id,
        user_id=current_user.id,
        content=req.content,
        parent_id=req.parent_id
    )
    
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    
    return comment

# GET /review/pending
@router.get("/pending", response_model=PaginatedResponse[RecommendationResponse])
async def get_pending_reviews(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Recommendation).where(Recommendation.status == RecommendationStatus.PENDING_REVIEW)
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0
    
    stmt = stmt.order_by(Recommendation.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    items = list(result.scalars().all())
    
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return {"items": items, "total": total, "page": page, "page_size": page_size, "total_pages": total_pages}

# GET /review/history
@router.get("/history", response_model=PaginatedResponse[RecommendationResponse])
async def get_review_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Recommendation).where(Recommendation.status.in_([RecommendationStatus.APPROVED, RecommendationStatus.REJECTED, RecommendationStatus.EXECUTED]))
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0
    
    stmt = stmt.order_by(Recommendation.reviewed_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    items = list(result.scalars().all())
    
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return {"items": items, "total": total, "page": page, "page_size": page_size, "total_pages": total_pages}

# GET /analytics/review
@router.get("/analytics/review", response_model=ReviewAnalytics)
async def get_review_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    approved_count = await db.scalar(select(func.count(Recommendation.id)).where(Recommendation.status == RecommendationStatus.APPROVED)) or 0
    rejected_count = await db.scalar(select(func.count(Recommendation.id)).where(Recommendation.status == RecommendationStatus.REJECTED)) or 0
    escalation_count = await db.scalar(select(func.count(Recommendation.id)).where(Recommendation.status == RecommendationStatus.ESCALATED)) or 0
    
    total = approved_count + rejected_count
    approval_rate = approved_count / total if total > 0 else 0.0

    
    return {
        "approval_rate": round(approval_rate, 2),
        "average_review_time_hours": 2.4, # Mocked
        "accuracy_rate": 0.88,           # Mocked
        "escalation_count": escalation_count
    }
