from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class KnowledgeDocumentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    document_type: str


class KnowledgeDocumentCreate(KnowledgeDocumentBase):
    uploaded_file: str
    uploaded_by: int
    file_hash: Optional[str] = None
    version: Optional[int] = 1
    status: Optional[str] = "pending"
    is_archived: Optional[bool] = False


class KnowledgeDocumentUpdate(BaseModel):
    title: Optional[str] = None
    document_type: Optional[str] = None
    status: Optional[str] = None
    is_archived: Optional[bool] = None
    version: Optional[int] = None


class KnowledgeDocumentResponse(BaseModel):
    id: int
    title: str
    document_type: str
    uploaded_file: str
    uploaded_by: int
    file_hash: Optional[str] = None
    version: int
    status: str
    is_archived: bool
    created_at: datetime

    class Config:
        from_attributes = True

