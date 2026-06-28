from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db, get_current_user
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse
from app.schemas.common import PaginatedResponse
from app.repositories.customer_repository import CustomerRepository
from app.services.audit_service import AuditService
from app.models.user import User

router = APIRouter()


@router.get("", response_model=PaginatedResponse[CustomerResponse])
async def list_customers(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    industry: Optional[str] = None, current_stage: Optional[str] = None,
    min_revenue: Optional[float] = None, max_revenue: Optional[float] = None,
    min_health_score: Optional[float] = None, max_health_score: Optional[float] = None,
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user),
):
    repo = CustomerRepository(db)
    items, total = await repo.search_customers(
        industry=industry, current_stage=current_stage,
        min_revenue=min_revenue, max_revenue=max_revenue,
        min_health_score=min_health_score, max_health_score=max_health_score,
        skip=(page - 1) * page_size, limit=page_size,
    )
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return {"items": items, "total": total, "page": page, "page_size": page_size, "total_pages": total_pages}


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = CustomerRepository(db)
    customer = await repo.get_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.post("", response_model=CustomerResponse, status_code=201)
async def create_customer(data: CustomerCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = CustomerRepository(db)
    audit = AuditService(db)
    customer = await repo.create(data.model_dump())
    await audit.log("create", "customer", customer.id, current_user.id)
    from app.redis.client import invalidate_recommendation_cache
    await invalidate_recommendation_cache()
    return customer


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(customer_id: int, data: CustomerUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = CustomerRepository(db)
    audit = AuditService(db)
    customer = await repo.update(customer_id, data.model_dump(exclude_unset=True))
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    await audit.log("update", "customer", customer_id, current_user.id)
    from app.redis.client import invalidate_recommendation_cache
    await invalidate_recommendation_cache()
    return customer


@router.delete("/{customer_id}", status_code=204)
async def delete_customer(customer_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    repo = CustomerRepository(db)
    audit = AuditService(db)
    deleted = await repo.delete(customer_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Customer not found")
    await audit.log("delete", "customer", customer_id, current_user.id)
    from app.redis.client import invalidate_recommendation_cache
    await invalidate_recommendation_cache()
