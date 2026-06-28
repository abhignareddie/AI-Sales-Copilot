from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, get_current_user
from app.schemas.memory import MemoryCreate, MemoryUpdate, MemoryResponse
from app.schemas.common import PaginatedResponse
from app.repositories.memory_repository import MemoryRepository
from app.services.audit_service import AuditService
from app.models.user import User

router = APIRouter()


@router.get("", response_model=PaginatedResponse[MemoryResponse])
async def list_memories(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), customer_id: Optional[int] = None, memory_type: Optional[str] = None, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = MemoryRepository(db)
    if customer_id:
        items, total = await repo.get_by_customer(customer_id, skip=(page - 1) * page_size, limit=page_size)
    elif memory_type:
        items, total = await repo.get_by_type(memory_type, skip=(page - 1) * page_size, limit=page_size)
    else:
        items, total = await repo.get_all(skip=(page - 1) * page_size, limit=page_size)
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return {"items": items, "total": total, "page": page, "page_size": page_size, "total_pages": total_pages}


@router.get("/{memory_id}", response_model=MemoryResponse)
async def get_memory(memory_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = MemoryRepository(db)
    memory = await repo.get_by_id(memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory


@router.post("", response_model=MemoryResponse, status_code=201)
async def create_memory(data: MemoryCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = MemoryRepository(db)
    audit = AuditService(db)
    memory = await repo.create(data.model_dump())
    await audit.log("create", "memory", memory.id, current_user.id)
    return memory


@router.put("/{memory_id}", response_model=MemoryResponse)
async def update_memory(memory_id: int, data: MemoryUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = MemoryRepository(db)
    audit = AuditService(db)
    memory = await repo.update(memory_id, data.model_dump(exclude_unset=True))
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    await audit.log("update", "memory", memory_id, current_user.id)
    return memory


@router.delete("/{memory_id}", status_code=204)
async def delete_memory(memory_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = MemoryRepository(db)
    audit = AuditService(db)
    deleted = await repo.delete(memory_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Memory not found")
    await audit.log("delete", "memory", memory_id, current_user.id)
