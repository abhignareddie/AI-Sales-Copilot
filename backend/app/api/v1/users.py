from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, get_current_user, require_role
from app.schemas.user import UserUpdate, UserResponse
from app.schemas.common import PaginatedResponse
from app.repositories.user_repository import UserRepository
from app.services.audit_service import AuditService
from app.models.user import User

router = APIRouter()


@router.get("", response_model=PaginatedResponse[UserResponse])
async def list_users(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: AsyncSession = Depends(get_db), current_user: User = Depends(require_role(["admin", "manager"]))):
    repo = UserRepository(db)
    items, total = await repo.get_all(skip=(page - 1) * page_size, limit=page_size)
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return {"items": items, "total": total, "page": page, "page_size": page_size, "total_pages": total_pages}


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, data: UserUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = UserRepository(db)
    audit = AuditService(db)
    user = await repo.update(user_id, data.model_dump(exclude_unset=True))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await audit.log("update", "user", user_id, current_user.id)
    return user


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_role(["admin"]))):
    repo = UserRepository(db)
    audit = AuditService(db)
    deleted = await repo.delete(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    await audit.log("delete", "user", user_id, current_user.id)
