from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field


class MemoryBase(BaseModel):
    customer_id: int
    memory_type: str = Field(..., min_length=1, max_length=100)
    memory_data: dict[str, Any]


class MemoryCreate(MemoryBase):
    pass


class MemoryUpdate(BaseModel):
    memory_type: Optional[str] = None
    memory_data: Optional[dict[str, Any]] = None


class MemoryResponse(BaseModel):
    id: int
    customer_id: int
    memory_type: str
    memory_data: dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True
