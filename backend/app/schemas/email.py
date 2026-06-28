from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class EmailBase(BaseModel):
    customer_id: int
    subject: str = Field(..., min_length=1, max_length=500)
    sender: str
    receiver: str
    body: Optional[str] = None


class EmailCreate(EmailBase):
    pass


class EmailUpdate(BaseModel):
    subject: Optional[str] = None
    sender: Optional[str] = None
    receiver: Optional[str] = None
    body: Optional[str] = None
    uploaded_file: Optional[str] = None


class EmailResponse(BaseModel):
    id: int
    customer_id: int
    subject: str
    sender: str
    receiver: str
    body: Optional[str] = None
    uploaded_file: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
