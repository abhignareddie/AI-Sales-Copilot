from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CustomerBase(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=255)
    contact_person: str = Field(..., min_length=1, max_length=255)
    email: str
    phone: Optional[str] = None
    industry: Optional[str] = None
    annual_revenue: Optional[float] = None
    company_size: Optional[int] = None
    current_stage: str = "prospect"
    health_score: float = 50.0


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    company_name: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    industry: Optional[str] = None
    annual_revenue: Optional[float] = None
    company_size: Optional[int] = None
    current_stage: Optional[str] = None
    health_score: Optional[float] = None


class CustomerResponse(BaseModel):
    id: int
    company_name: str
    contact_person: str
    email: str
    phone: Optional[str] = None
    industry: Optional[str] = None
    annual_revenue: Optional[float] = None
    company_size: Optional[int] = None
    current_stage: str
    health_score: float
    created_at: datetime

    class Config:
        from_attributes = True
