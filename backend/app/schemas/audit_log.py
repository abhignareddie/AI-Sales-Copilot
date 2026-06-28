from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AuditLogCreate(BaseModel):
    user_id: Optional[int] = None
    action: str
    entity: str
    entity_id: Optional[int] = None


class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    action: str
    entity: str
    entity_id: Optional[int] = None
    timestamp: datetime

    class Config:
        from_attributes = True
