from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class MeetingBase(BaseModel):
    customer_id: int
    title: str = Field(..., min_length=1, max_length=255)
    transcript: Optional[str] = None
    meeting_date: datetime
    summary: Optional[str] = None


class MeetingCreate(MeetingBase):
    pass


class MeetingUpdate(BaseModel):
    title: Optional[str] = None
    transcript: Optional[str] = None
    meeting_date: Optional[datetime] = None
    summary: Optional[str] = None
    uploaded_file: Optional[str] = None


class MeetingResponse(BaseModel):
    id: int
    customer_id: int
    title: str
    transcript: Optional[str] = None
    meeting_date: datetime
    uploaded_file: Optional[str] = None
    summary: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
