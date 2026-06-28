from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class SupportTicketBase(BaseModel):
    customer_id: int
    ticket_number: str = Field(..., min_length=1, max_length=50)
    priority: str = "medium"
    status: str = "open"
    issue: str = Field(..., min_length=1)
    resolution: Optional[str] = None


class SupportTicketCreate(SupportTicketBase):
    pass


class SupportTicketUpdate(BaseModel):
    priority: Optional[str] = None
    status: Optional[str] = None
    issue: Optional[str] = None
    resolution: Optional[str] = None


class SupportTicketResponse(BaseModel):
    id: int
    customer_id: int
    ticket_number: str
    priority: str
    status: str
    issue: str
    resolution: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
