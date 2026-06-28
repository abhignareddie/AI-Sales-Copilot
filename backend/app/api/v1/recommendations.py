import time
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.customer import Customer
from app.models.support_ticket import SupportTicket
from app.models.meeting import Meeting
from app.models.email import Email
from app.models.recommendation import Recommendation, RecommendationStatus
from app.repositories.recommendation_repository import RecommendationRepository
from app.services.audit_service import AuditService
from app.schemas.recommendation import (
    RecommendationResponse,
    GenerateRequest,
    ModifyRequest,
    ActionRequest,
    SimulationRequest,
    SimulationResult,
    DashboardData
)
from app.schemas.common import PaginatedResponse
from app.services.decision_engine import (
    BusinessRuleEngine,
    RiskAnalysisEngine,
    OpportunityAnalysisEngine,
    ConfidenceEngine,
    ExplainabilityEngine,
    WhatIfSimulator
)

router = APIRouter()

# GET /recommendations
@router.get("", response_model=PaginatedResponse[RecommendationResponse])
async def list_recommendations(
    page: int = Query(1, ge=1), 
    page_size: int = Query(20, ge=1, le=100), 
    customer_id: Optional[int] = None, 
    status: Optional[str] = None, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    repo = RecommendationRepository(db)
    items, total = await repo.search_recommendations(customer_id=customer_id, status=status, skip=(page - 1) * page_size, limit=page_size)
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return {"items": items, "total": total, "page": page, "page_size": page_size, "total_pages": total_pages}

# GET /recommendations/customer/{id}
@router.get("/customer/{customer_id}", response_model=List[RecommendationResponse])
async def get_customer_recommendations(
    customer_id: int, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    stmt = select(Recommendation).where(
        and_(
            Recommendation.customer_id == customer_id,
            Recommendation.status == "pending"
        )
    ).order_by(Recommendation.confidence.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())

# GET /recommendations/history
@router.get("/history", response_model=PaginatedResponse[RecommendationResponse])
async def get_recommendation_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Recommendation).where(Recommendation.status.in_(["approved", "rejected", "implemented"]))
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0
    
    stmt = stmt.order_by(Recommendation.reviewed_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    items = list(result.scalars().all())
    
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return {"items": items, "total": total, "page": page, "page_size": page_size, "total_pages": total_pages}

# GET /recommendations/dashboard
@router.get("/dashboard", response_model=DashboardData)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Total counts by status
    status_counts = {}
    for status in [RecommendationStatus.PENDING_REVIEW, RecommendationStatus.APPROVED, RecommendationStatus.REJECTED, RecommendationStatus.EXECUTED]:
        count = await db.scalar(select(func.count(Recommendation.id)).where(Recommendation.status == status)) or 0
        status_counts[status.value] = count
        
    total_reviewed = status_counts[RecommendationStatus.APPROVED.value] + status_counts[RecommendationStatus.REJECTED.value] + status_counts[RecommendationStatus.EXECUTED.value]
    approval_rate = (status_counts[RecommendationStatus.APPROVED.value] + status_counts[RecommendationStatus.EXECUTED.value]) / total_reviewed if total_reviewed > 0 else 0.0

    
    avg_confidence = await db.scalar(select(func.avg(Recommendation.confidence))) or 0.5
    
    return {
        "recommendation_status": status_counts,
        "approval_rate": round(approval_rate, 2),
        "average_confidence": round(float(avg_confidence), 2),
        "business_impact_summary": {"high": 12, "medium": 8, "low": 3}, # Mocked
        "top_risks": [
            {"risk": "Competitor Activity", "count": 4},
            {"risk": "Pending support issues", "count": 2}
        ],
        "top_opportunities": [
            {"opportunity": "Expansion", "value": 75000.0},
            {"opportunity": "Contract Renewal", "value": 25000.0}
        ],
        "roi_summary": 128500.0
    }

# POST /recommendations/generate
@router.post("/generate", response_model=List[RecommendationResponse])
async def generate_recommendations(
    req: GenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Fetch customer
    customer = await db.get(Customer, req.customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    customer_dict = {
        "id": customer.id,
        "company_name": customer.company_name,
        "current_stage": customer.current_stage,
        "health_score": customer.health_score,
        "annual_revenue": customer.annual_revenue,
        "company_size": customer.company_size,
    }
    
    # 2. Gather context metrics
    tickets_count = await db.scalar(
        select(func.count(SupportTicket.id)).where(
            and_(
                SupportTicket.customer_id == customer.id,
                SupportTicket.status == "open"
            )
        )
    ) or 0
    
    # Check for competitor mentions in meeting transcripts / emails
    competitor_detected = False
    competitor_keywords = ["gong", "chorus", "salesloft", "outreach", "clari"]
    for kw in competitor_keywords:
        meetings_match = await db.scalar(
            select(func.count(Meeting.id)).where(
                and_(
                    Meeting.customer_id == customer.id,
                    Meeting.transcript.ilike(f"%{kw}%")
                )
            )
        ) or 0
        emails_match = await db.scalar(
            select(func.count(Email.id)).where(
                and_(
                    Email.customer_id == customer.id,
                    Email.body.ilike(f"%{kw}%")
                )
            )
        ) or 0
        if meetings_match > 0 or emails_match > 0:
            competitor_detected = True
            break
            
    context = {
        "support_tickets_count": tickets_count,
        "competitor_detected": competitor_detected
    }
    
    # 3. Fetch telemetry metrics
    meetings_stmt = select(Meeting).where(Meeting.customer_id == customer.id).limit(3)
    meetings_res = await db.execute(meetings_stmt)
    meetings_list_objs = [{"title": m.title, "summary": m.summary, "meeting_date": str(m.meeting_date)} for m in meetings_res.scalars().all()]
    
    emails_stmt = select(Email).where(Email.customer_id == customer.id).limit(5)
    emails_res = await db.execute(emails_stmt)
    emails_list_objs = [{"subject": e.subject, "sender": e.sender, "receiver": e.receiver} for e in emails_res.scalars().all()]
    
    tickets_stmt = select(SupportTicket).where(and_(SupportTicket.customer_id == customer.id, SupportTicket.status == "open"))
    tickets_res = await db.execute(tickets_stmt)
    tickets_list_objs = [{"ticket_number": t.ticket_number, "priority": t.priority, "issue": t.issue, "status": t.status} for t in tickets_res.scalars().all()]

    rule_engine = BusinessRuleEngine()
    rule_matches = rule_engine.evaluate(customer_dict, context)

    from app.services.context_builder import ContextBuilder
    context_str = ContextBuilder.build_full_context(
        customer_data=customer_dict,
        meetings=meetings_list_objs,
        emails=emails_list_objs,
        support_tickets=tickets_list_objs,
        memories=[],
        knowledge_docs=[],
        business_rules=rule_matches,
        timeline=[]
    )

    from app.services.llm_factory import LLMFactory
    llm = LLMFactory.get_llm()
    
    # Query Gemini for Next Best Action using the assembled context
    nba_data = await llm.recommend_next_action(customer_dict, context_str)
    
    # Map Gemini reasoning output to database recommendation models
    recommendations_list = []
    
    # 1. Main Recommended Action
    primary_details = {
        "title": "Gemini Decision Action",
        "priority": nba_data.get("risk_level", "medium").lower(),
        "reason": nba_data.get("reasoning", "Recommended based on account telemetry"),
        "evidence": nba_data.get("citations", ["Customer telemetry data"]),
        "business_impact": "high" if nba_data.get("risk_level") == "High" else "medium",
        "estimated_roi": nba_data.get("estimated_roi", "$5,000"),
        "expected_outcome": "Improved partner relationship alignment",
        "suggested_timeline": "immediate" if nba_data.get("risk_level") == "High" else "this_week",
        "alternatives": nba_data.get("alternative_actions", []),
        "explainability": {
            "why_this_action": nba_data.get("reasoning"),
            "evidence_details": nba_data.get("citations", []),
            "supporting_knowledge_docs": [nba_data.get("knowledge_used", "policy_renewal.pdf")],
            "supporting_meetings": [m["title"] for m in meetings_list_objs],
            "supporting_crm_fields": ["health_score", "current_stage"],
            "rejected_alternatives_rationale": nba_data.get("review_notes", "")
        }
    }
    
    rec1 = Recommendation(
        customer_id=customer.id,
        recommendation=nba_data.get("recommended_action", "Offer bundle pricing renewal proposal"),
        confidence=nba_data.get("confidence", 0.92),
        evidence=nba_data.get("reasoning", "Identified high-priority renewal path"),
        status=RecommendationStatus.PENDING_REVIEW,
        details=primary_details
    )
    db.add(rec1)
    recommendations_list.append(rec1)
    
    # 2. Add alternative options as separate recommendation cards
    alt_actions = nba_data.get("alternative_actions", [])
    for idx, alt in enumerate(alt_actions[:4]):
        alt_details = {
            "title": alt.get("title", f"Alternative option #{idx+1}"),
            "priority": "medium",
            "reason": "Secondary recommendation path identified by Gemini reasoning engine",
            "evidence": nba_data.get("citations", []),
            "business_impact": "medium",
            "estimated_roi": alt.get("roi", "$2,500"),
            "expected_outcome": "Alternative resolution optimization",
            "suggested_timeline": "this_week",
            "alternatives": [],
            "explainability": {
                "why_this_action": f"Alternative scenario based on customer profile stage: {customer.current_stage}",
                "evidence_details": ["Account historical timeline"],
                "supporting_knowledge_docs": [],
                "supporting_meetings": [],
                "supporting_crm_fields": ["current_stage"],
                "rejected_alternatives_rationale": f"Success rate is estimated at {int(alt.get('success_rate', 0.7)*100)}%"
            }
        }
        rec_alt = Recommendation(
            customer_id=customer.id,
            recommendation=alt.get("title", "Alternative outreach action"),
            confidence=nba_data.get("confidence", 0.8) - 0.05 * (idx + 1),
            evidence=f"Alternative path with projected success rate of {alt.get('success_rate', 0.75)}",
            status=RecommendationStatus.PENDING_REVIEW,
            details=alt_details
        )
        db.add(rec_alt)
        recommendations_list.append(rec_alt)
        
    await db.commit()
    for r in recommendations_list:
        await db.refresh(r)
        
    audit = AuditService(db)
    await audit.log("generate_recommendations", "customer", customer.id, current_user.id)
    return recommendations_list

# POST /recommendations/approve
@router.post("/approve", response_model=RecommendationResponse)
async def approve_recommendation(
    req: ActionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rec = await db.get(Recommendation, req.recommendation_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
        
    rec.status = RecommendationStatus.APPROVED
    rec.approved_by = current_user.id
    rec.reviewer_id = current_user.id
    rec.reviewed_at = datetime.now(timezone.utc)
    rec.comments = req.comments
    
    await db.commit()
    await db.refresh(rec)
    
    audit = AuditService(db)
    await audit.log("approve", "recommendation", rec.id, current_user.id)
    return rec

# POST /recommendations/reject
@router.post("/reject", response_model=RecommendationResponse)
async def reject_recommendation(
    req: ActionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rec = await db.get(Recommendation, req.recommendation_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
        
    rec.status = RecommendationStatus.REJECTED
    rec.reviewer_id = current_user.id
    rec.reviewed_at = datetime.now(timezone.utc)
    rec.comments = req.comments
    
    await db.commit()
    await db.refresh(rec)
    
    audit = AuditService(db)
    await audit.log("reject", "recommendation", rec.id, current_user.id)
    return rec

# POST /recommendations/modify
@router.post("/modify", response_model=RecommendationResponse)
async def modify_recommendation(
    req: ModifyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rec = await db.get(Recommendation, req.recommendation_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
        
    rec.recommendation = req.recommendation
    rec.comments = req.comments
    rec.reviewer_id = current_user.id
    rec.reviewed_at = datetime.now(timezone.utc)
    rec.status = RecommendationStatus.APPROVED # Modified results in approval
    
    await db.commit()
    await db.refresh(rec)
    
    audit = AuditService(db)
    await audit.log("modify", "recommendation", rec.id, current_user.id)
    return rec

# POST /recommendations/simulate
@router.post("/simulate", response_model=SimulationResult)
async def simulate_recommendation(
    req: SimulationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    customer = await db.get(Customer, req.customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    customer_dict = {
        "id": customer.id,
        "company_name": customer.company_name,
        "current_stage": customer.current_stage,
        "health_score": customer.health_score,
        "annual_revenue": customer.annual_revenue,
        "company_size": customer.company_size,
    }
    
    simulator = WhatIfSimulator()
    res = simulator.simulate(customer_dict, req.parameter, req.value)
    
    audit = AuditService(db)
    await audit.log("simulate_whatif", "customer", customer.id, current_user.id)
    return res

# GET /recommendations/{rec_id}
@router.get("/{rec_id}", response_model=RecommendationResponse)
async def get_recommendation(
    rec_id: int, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    rec = await db.get(Recommendation, rec_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return rec
