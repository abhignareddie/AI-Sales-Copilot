from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.memory_entry import MemoryEntry
from app.services.memory_service import MemoryManager

router = APIRouter()

class MemorySearchRequest(BaseModel):
    customer_id: int
    query: str
    limit: Optional[int] = 5

class MemorySearchResponse(BaseModel):
    id: int
    memory_type: str
    content: str
    relevance_score: float
    created_at: str

class TimelineItem(BaseModel):
    type: str
    title: str
    description: str
    timestamp: str
    meta: dict

# GET /memory/customer/{id}
@router.get("/memory/customer/{customer_id}")
async def get_customer_memories(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(MemoryEntry).where(MemoryEntry.customer_id == customer_id).order_by(MemoryEntry.created_at.desc())
    result = await db.execute(stmt)
    memories = result.scalars().all()
    return memories

# POST /memory/search
@router.post("/memory/search")
async def search_memory(

    req: MemorySearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    manager = MemoryManager(db)
    results = await manager.retrieve_relevant_memories(
        customer_id=req.customer_id,
        query=req.query,
        limit=req.limit or 5
    )
    # Convert datetime to string for clean serialization
    serialized = []
    for r in results:
        serialized.append({
            "id": r["id"],
            "memory_type": r["memory_type"],
            "content": r["content"],
            "relevance_score": r["relevance_score"],
            "created_at": r["created_at"].isoformat()
        })
    return serialized

# GET /timeline/customer/{id}
@router.get("/timeline/customer/{customer_id}", response_model=List[TimelineItem])
async def get_customer_timeline(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    manager = MemoryManager(db)
    items = await manager.generate_timeline(customer_id)
    
    # Format datetimes
    formatted = []
    for item in items:
        formatted.append({
            "type": item["type"],
            "title": item["title"],
            "description": item["description"],
            "timestamp": item["timestamp"].isoformat(),
            "meta": item["meta"]
        })
    return formatted
