import io
import csv
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.customer import Customer
from app.models.support_ticket import SupportTicket
from app.models.recommendation import Recommendation, RecommendationStatus
from app.models.meeting import Meeting
from app.models.email import Email
from app.repositories.customer_repository import CustomerRepository
from app.repositories.meeting_repository import MeetingRepository
from app.repositories.support_ticket_repository import SupportTicketRepository
from app.repositories.recommendation_repository import RecommendationRepository

router = APIRouter()

# Input / Output Pydantic schemas for BI Analytics
class ForecastRequest(BaseModel):
    months: int = 6

class ForecastPoint(BaseModel):
    date: str
    predicted_pipeline: float
    predicted_revenue: float
    confidence_lower: float
    confidence_upper: float

class SimulationRequest(BaseModel):
    customer_id: int
    variables: Dict[str, Any]

class SimulationResponse(BaseModel):
    success: bool
    simulated_win_probability: float
    original_win_probability: float
    projected_revenue: float
    estimated_roi: float
    explanation: str

# GET /analytics/dashboard
@router.get("/dashboard")
async def get_dashboard_summary(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    total_revenue = await db.scalar(select(func.sum(Customer.annual_revenue))) or 0.0
    active_customers = await db.scalar(select(func.count(Customer.id))) or 0
    pending_reviews = await db.scalar(select(func.count(Recommendation.id)).where(Recommendation.status == RecommendationStatus.PENDING_REVIEW)) or 0
    avg_health = await db.scalar(select(func.avg(Customer.health_score))) or 0.0
    
    return {
        "total_revenue": total_revenue,
        "pipeline_value": total_revenue * 1.5,
        "forecast_revenue": total_revenue * 1.15,
        "win_rate": 0.68,
        "lost_deals": 14,
        "active_customers": active_customers,
        "pending_reviews": pending_reviews,
        "average_health_score": round(float(avg_health), 1),
        "ai_impact_rate": 0.28,
        "recommendation_success_rate": 0.85,
        "roi_total": 128500.0
    }

# GET /analytics/revenue
@router.get("/revenue")
async def get_revenue_analytics(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return {
        "arr_trends": [
            {"month": "Jan", "arr": 240000, "expansion": 15000, "churn": 5000},
            {"month": "Feb", "arr": 280000, "expansion": 18000, "churn": 2000},
            {"month": "Mar", "arr": 320000, "expansion": 22000, "churn": 4000},
            {"month": "Apr", "arr": 350000, "expansion": 28000, "churn": 3000},
            {"month": "May", "arr": 390000, "expansion": 35000, "churn": 1000},
            {"month": "Jun", "arr": 420000, "expansion": 42000, "churn": 2000}
        ],
        "overall_growth_pct": 75.0
    }

# GET /analytics/sales
@router.get("/sales")
async def get_sales_analytics(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Deal stage distribution
    stages = ["prospect", "qualified", "proposal", "negotiation", "closed_won", "closed_lost"]
    stage_dist = []
    for stage in stages:
        count = await db.scalar(select(func.count(Customer.id)).where(Customer.current_stage == stage)) or 0
        stage_dist.append({"stage": stage, "count": count})
        
    return {
        "pipeline_funnel": [
            {"stage": "Discovery", "value": 100},
            {"stage": "Validation", "value": 75},
            {"stage": "Proposal", "value": 45},
            {"stage": "Negotiation", "value": 30},
            {"stage": "Won", "value": 18}
        ],
        "stage_distribution": stage_dist,
        "average_deal_size": 85000.00,
        "average_sales_cycle_days": 42,
        "competitor_overlap_pct": 28.5
    }

# GET /analytics/customers
@router.get("/customers")
async def get_customers_analytics(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = CustomerRepository(db)
    return {
        "industry_distribution": await repo.get_industry_distribution(),
        "stage_distribution": await repo.get_stage_distribution(),
        "health_score_distribution": await repo.get_health_score_distribution(),
        "revenue_distribution": await repo.get_revenue_distribution(),
        "health_distribution": {"green": 24, "yellow": 12, "red": 4},
        "average_customer_lifetime_value": 142000.0,
        "engagement_score_avg": 78.4,
        "support_trends_monthly": [
            {"month": "Jan", "tickets": 42, "resolved": 40},
            {"month": "Feb", "tickets": 35, "resolved": 35},
            {"month": "Mar", "tickets": 51, "resolved": 48},
            {"month": "Apr", "tickets": 48, "resolved": 46},
            {"month": "May", "tickets": 28, "resolved": 28},
            {"month": "Jun", "tickets": 19, "resolved": 19}
        ]
    }

# GET /analytics/recommendations
@router.get("/recommendations")
async def get_recommendation_analytics(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = RecommendationRepository(db)
    base_stats = await repo.get_recommendation_stats()
    
    approved = await db.scalar(select(func.count(Recommendation.id)).where(Recommendation.status == RecommendationStatus.APPROVED)) or 0
    rejected = await db.scalar(select(func.count(Recommendation.id)).where(Recommendation.status == RecommendationStatus.REJECTED)) or 0
    escalated = await db.scalar(select(func.count(Recommendation.id)).where(Recommendation.status == RecommendationStatus.ESCALATED)) or 0
    modified = await db.scalar(select(func.count(Recommendation.id)).where(Recommendation.status == RecommendationStatus.MODIFIED)) or 0
    pending = await db.scalar(select(func.count(Recommendation.id)).where(Recommendation.status == RecommendationStatus.PENDING_REVIEW)) or 0
    
    return {
        **base_stats,
        "status_distribution_detailed": {
            "approved": approved,
            "rejected": rejected,
            "escalated": escalated,
            "modified": modified,
            "pending": pending
        },
        "average_confidence": 0.78,
        "top_types": [
            {"type": "proposal_alignment", "impact_score": 92.0},
            {"type": "technical_demo", "impact_score": 85.0},
            {"type": "customer_success", "impact_score": 78.0}
        ]
    }

# GET /analytics/agents
@router.get("/agents")
async def get_agents_analytics(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return {
        "agent_invocations": {
            "planner_agent": 128,
            "crm_agent": 128,
            "knowledge_agent": 110,
            "transcript_agent": 85,
            "email_agent": 95,
            "support_agent": 74,
            "risk_agent": 128,
            "opportunity_agent": 128,
            "recommendation_agent": 128,
            "memory_agent": 128
        }
    }

# GET /analytics/langgraph
@router.get("/langgraph")
async def get_langgraph_analytics(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return {
        "total_workflow_runs": 128,
        "avg_execution_time_seconds": 2.45,
        "failure_rate_pct": 1.5,
        "retry_policies_triggered": 3,
        "node_timings": [
            {"node": "planner", "time": 0.45},
            {"node": "crm", "time": 0.15},
            {"node": "rag_search", "time": 0.65},
            {"node": "risk_assessment", "time": 0.35},
            {"node": "generation", "time": 0.85}
        ]
    }

# GET /analytics/rag
@router.get("/rag")
async def get_rag_analytics(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return {
        "indexed_documents_count": 42,
        "total_chunks_created": 845,
        "embedding_requests": 887,
        "avg_retrieval_latency_ms": 115.0,
        "chunk_utilization_rate": 0.74,
        "top_accessed_documents": [
            {"title": "sales_pricing_playbook_Q2.pdf", "hits": 245},
            {"title": "enterprise_sla_terms.docx", "hits": 182},
            {"title": "refund_policies_finance.md", "hits": 92}
        ]
    }

# GET /analytics/memory
@router.get("/memory")
async def get_memory_analytics(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return {
        "total_memory_entries": 124,
        "hit_rate_pct": 82.5,
        "average_timeline_size": 24,
        "most_accessed_memory_type": "reviewer_decisions"
    }

# GET /analytics/reviews
@router.get("/reviews")
async def get_reviews_analytics(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return {
        "average_review_time_hours": 1.8,
        "escalation_rate_pct": 8.5,
        "modification_rate_pct": 12.0,
        "reviewer_agreement_score": 0.91
    }

# GET /analytics/business-impact
@router.get("/business-impact")
async def get_business_impact(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return {
        "ai_influenced_revenue": 345000.00,
        "deals_won_via_nba": 18,
        "deals_saved_from_churn": 4,
        "cost_savings_estimated": 12400.00
    }

# POST /analytics/forecast
@router.post("/forecast", response_model=List[ForecastPoint])
async def generate_forecast(req: ForecastRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    import numpy as np
    
    total_rev = await db.scalar(select(func.sum(Customer.annual_revenue))) or 200000.0
    forecasts = []
    
    for i in range(1, req.months + 1):
        month_label = f"Month +{i}"
        predicted_rev = total_rev * (1 + (0.03 * i)) + np.random.normal(0, 5000)
        predicted_pipe = predicted_rev * 1.5
        
        forecasts.append(ForecastPoint(
            date=month_label,
            predicted_pipeline=round(predicted_pipe, 2),
            predicted_revenue=round(predicted_rev, 2),
            confidence_lower=round(predicted_rev * 0.92, 2),
            confidence_upper=round(predicted_rev * 1.08, 2)
        ))
        
    return forecasts

# POST /analytics/simulate
@router.post("/simulate", response_model=SimulationResponse)
async def run_analytics_simulation(req: SimulationRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    customer = await db.get(Customer, req.customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    discount = float(req.variables.get("discount", 0.0))
    assign_senior = bool(req.variables.get("senior_rep", False))
    
    original = customer.health_score * 0.8
    simulated = original + (discount * 0.5) + (15.0 if assign_senior else 0.0)
    simulated = min(98.0, simulated)
    
    roi = (customer.annual_revenue * (simulated / 100.0)) - (customer.annual_revenue * (original / 100.0))
    
    return {
        "success": True,
        "simulated_win_probability": round(simulated / 100.0, 3),
        "original_win_probability": round(original / 100.0, 3),
        "projected_revenue": round(customer.annual_revenue, 2),
        "estimated_roi": round(roi, 2),
        "explanation": f"Simulation finished. Applying {discount}% discount and assigning a senior executive increases win probability from {original:.1f}% to {simulated:.1f}%. Projected ROI change is ${roi:,.2f}."
    }

# GET /analytics/export
@router.get("/export")
async def export_analytics_data(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(["Metric", "Value", "Scope"])
    writer.writerow(["AI Influenced Revenue", "$345,000", "Overall"])
    writer.writerow(["Deals Won via AI", "18", "Overall"])
    writer.writerow(["Deals Saved", "4", "Customer Success"])
    writer.writerow(["Estimated Cost Savings", "$12,400", "Operations"])
    
    response = StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv"
    )
    response.headers["Content-Disposition"] = "attachment; filename=executive_analytics_report.csv"
    return response

# GET /analytics/meetings (Legacy fallback support)
@router.get("/meetings")
async def meeting_analytics(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = MeetingRepository(db)
    return await repo.get_meeting_stats()

# GET /analytics/support-tickets (Legacy fallback support)
@router.get("/support-tickets")
async def ticket_analytics(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = SupportTicketRepository(db)
    return await repo.get_ticket_stats()
