from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    email: str
    role: str = "sales_rep"


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    avatar: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    role: str
    avatar: Optional[str] = None
    mfa_enabled: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
