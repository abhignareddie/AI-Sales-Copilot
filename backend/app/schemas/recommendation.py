from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class RecommendationBase(BaseModel):
    customer_id: int
    recommendation: str = Field(..., min_length=1)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence: Optional[str] = None
    status: str = "pending"

class RecommendationCreate(RecommendationBase):
    details: Optional[Dict[str, Any]] = None
    feedback: Optional[str] = None

class RecommendationUpdate(BaseModel):
    recommendation: Optional[str] = None
    confidence: Optional[float] = None
    evidence: Optional[str] = None
    status: Optional[str] = None
    approved_by: Optional[int] = None
    reviewer_id: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    comments: Optional[str] = None
    feedback: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class RecommendationResponse(BaseModel):
    id: int
    customer_id: int
    recommendation: str
    confidence: float
    evidence: Optional[str] = None
    status: str
    approved_by: Optional[int] = None
    reviewer_id: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    comments: Optional[str] = None
    feedback: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Action requests
class GenerateRequest(BaseModel):
    customer_id: int
    business_goal: Optional[str] = None
    namespace: str = "default"

class ModifyRequest(BaseModel):
    recommendation_id: int
    recommendation: str
    comments: Optional[str] = None

class ActionRequest(BaseModel):
    recommendation_id: int
    comments: Optional[str] = None

class SimulationRequest(BaseModel):
    customer_id: int
    parameter: str # e.g. "discount", "delay_weeks"
    value: Any     # e.g. 15, 1

class SimulationResult(BaseModel):
    customer_id: int
    parameter: str
    original_value: Any
    simulated_value: Any
    original_probability: float
    simulated_probability: float
    estimated_roi: float
    business_impact: str
    explanation: str

class DashboardData(BaseModel):
    recommendation_status: Dict[str, int]
    approval_rate: float
    average_confidence: float
    business_impact_summary: Dict[str, int]
    top_risks: List[Dict[str, Any]]
    top_opportunities: List[Dict[str, Any]]
    roi_summary: float

class GeminiRecommendationSchema(BaseModel):
    customer_id: int
    summary: str
    customer_health: int
    risk_level: str
    engagement_score: int
    recommended_action: str
    alternative_actions: List[Dict[str, Any]]
    citations: List[str]
    confidence: float
    estimated_roi: str
    reasoning: str
    memory_used: str
    knowledge_used: str
    business_rules: str
    review_notes: str

