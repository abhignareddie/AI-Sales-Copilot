import time
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.core.dependencies import get_db, get_current_user
from app.schemas.knowledge_document import (
    KnowledgeDocumentCreate, 
    KnowledgeDocumentUpdate, 
    KnowledgeDocumentResponse
)
from app.schemas.common import PaginatedResponse
from app.repositories.knowledge_repository import KnowledgeRepository
from app.services.audit_service import AuditService
from app.utils.file_upload import save_upload_file
from app.models.user import User
from app.models.knowledge_document import KnowledgeDocument
from app.rag.manager import RAGManager
from app.rag.background_tasks import async_index_document

router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    namespace: str = "default"
    top_k: int = 5
    filters: Optional[dict] = None
    version: Optional[str] = None

class SearchResultItem(BaseModel):
    content: str
    metadata: dict
    similarity_score: Optional[float] = None
    bm25_score: Optional[float] = None
    rrf_score: Optional[float] = None
    rerank_score: Optional[float] = None

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResultItem]
    latency_seconds: float
    explainability: dict

class StatusResponse(BaseModel):
    total_documents: int
    active_documents: int
    archived_documents: int
    indexing_documents: int
    failed_documents: int
    average_latency_ms: float

# GET /knowledge/documents
@router.get("/documents", response_model=PaginatedResponse[KnowledgeDocumentResponse])
async def get_documents(
    page: int = Query(1, ge=1), 
    page_size: int = Query(20, ge=1, le=100), 
    document_type: Optional[str] = None, 
    status: Optional[str] = None,
    q: Optional[str] = None, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    stmt = select(KnowledgeDocument)
    filters = []
    if q:
        filters.append(KnowledgeDocument.title.ilike(f"%{q}%"))
    if document_type:
        filters.append(KnowledgeDocument.document_type == document_type)
    if status:
        filters.append(KnowledgeDocument.status == status)
    if filters:
        stmt = stmt.where(and_(*filters))
        
    count_result = await db.execute(select(func.count()).select_from(stmt.subquery()))
    total = count_result.scalar() or 0
    
    stmt = stmt.order_by(KnowledgeDocument.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    items = list(result.scalars().all())
    
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return {"items": items, "total": total, "page": page, "page_size": page_size, "total_pages": total_pages}

# Legacy/Alternative list endpoint
@router.get("", response_model=PaginatedResponse[KnowledgeDocumentResponse])
async def list_documents(
    page: int = Query(1, ge=1), 
    page_size: int = Query(20, ge=1, le=100), 
    document_type: Optional[str] = None, 
    q: Optional[str] = None, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    return await get_documents(page=page, page_size=page_size, document_type=document_type, q=q, db=db, current_user=current_user)

# GET /knowledge/status
@router.get("/status", response_model=StatusResponse)
async def get_status(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    total_count = await db.scalar(select(func.count(KnowledgeDocument.id))) or 0
    active_count = await db.scalar(select(func.count(KnowledgeDocument.id)).where(KnowledgeDocument.is_archived == False)) or 0
    archived_count = await db.scalar(select(func.count(KnowledgeDocument.id)).where(KnowledgeDocument.is_archived == True)) or 0
    indexing_count = await db.scalar(select(func.count(KnowledgeDocument.id)).where(KnowledgeDocument.status == "processing")) or 0
    failed_count = await db.scalar(select(func.count(KnowledgeDocument.id)).where(KnowledgeDocument.status == "failed")) or 0
    
    return {
        "total_documents": total_count,
        "active_documents": active_count,
        "archived_documents": archived_count,
        "indexing_documents": indexing_count,
        "failed_documents": failed_count,
        "average_latency_ms": 12.5 # Mock/Traced value
    }

# POST /knowledge/search
@router.post("/search", response_model=SearchResponse)
async def search_knowledge(
    req: SearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    start_time = time.time()
    
    manager = RAGManager(db)
    # Perform Search
    results = manager.hybrid_searcher.search(
        namespace=req.namespace,
        query=req.query,
        top_k=req.top_k,
        filters=req.filters,
        version=req.version
    )
    
    latency = time.time() - start_time
    
    # Format explainability details
    explainability = {
        "fusion_algorithm": "Reciprocal Rank Fusion (RRF)",
        "rrf_constant_k": 60,
        "rerank_algorithm": "CrossEncoder Sim / MS-MARCO-MiniLM",
        "latency_seconds": round(latency, 4)
    }
    
    return {
        "query": req.query,
        "results": results,
        "latency_seconds": round(latency, 4),
        "explainability": explainability
    }

# POST /knowledge/upload
@router.post("/upload", response_model=KnowledgeDocumentResponse, status_code=201)
async def upload_document(
    background_tasks: BackgroundTasks,
    title: str = Query(...),
    chunk_strategy: str = Query("recursive"),
    namespace: str = Query("default"),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Save file to uploads folder
    file_meta = await save_upload_file(file, subfolder="knowledge")
    ext = file_meta["extension"].lstrip(".")
    
    # Calculate checksum/hash
    import hashlib
    with open(file_meta["file_path"], "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
        
    manager = RAGManager(db)
    
    # Check duplicate
    dup = await manager.check_duplicate(file_hash)
    if dup:
        # Instead of failing, return the existing document to be idempotent/explain duplicate
        audit = AuditService(db)
        await audit.log("upload_duplicate", "knowledge_document", dup.id, current_user.id)
        if dup.status == "failed":
            dup.status = "pending"
            await db.commit()
            background_tasks.add_task(
                async_index_document, 
                doc_id=dup.id, 
                namespace=namespace, 
                chunk_strategy=chunk_strategy
            )
        return dup
        
    # Create DB entry
    doc = await manager.create_document_metadata(
        title=title,
        doc_type=ext,
        file_path=file_meta["file_path"],
        uploaded_by=current_user.id,
        file_hash=file_hash
    )
    
    # Trigger background tasks for parsing/indexing
    background_tasks.add_task(
        async_index_document, 
        doc_id=doc.id, 
        namespace=namespace, 
        chunk_strategy=chunk_strategy
    )
    
    audit = AuditService(db)
    await audit.log("upload", "knowledge_document", doc.id, current_user.id)
    return doc

# DELETE /knowledge/document/{id} or /knowledge/{id}
@router.delete("/document/{doc_id}", status_code=204)
async def delete_document_path(
    doc_id: int, 
    namespace: str = Query("default"),
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    manager = RAGManager(db)
    success = await manager.archive_document(doc_id, namespace)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    audit = AuditService(db)
    await audit.log("archive", "knowledge_document", doc_id, current_user.id)

@router.delete("/{doc_id}", status_code=204)
async def delete_document_legacy(
    doc_id: int, 
    namespace: str = Query("default"),
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    return await delete_document_path(doc_id=doc_id, namespace=namespace, db=db, current_user=current_user)

# POST /knowledge/reindex
@router.post("/reindex")
async def trigger_reindex(
    background_tasks: BackgroundTasks,
    namespace: str = Query("default"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Find all active documents
    stmt = select(KnowledgeDocument).where(KnowledgeDocument.is_archived == False)
    result = await db.execute(stmt)
    docs = result.scalars().all()
    
    for doc in docs:
        background_tasks.add_task(
            async_index_document,
            doc_id=doc.id,
            namespace=namespace
        )
        
    audit = AuditService(db)
    await audit.log("reindex_all", "knowledge_document", 0, current_user.id)
    return {"success": True, "message": f"Reindexing started for {len(docs)} documents"}

# GET /knowledge/{doc_id}
@router.get("/{doc_id}", response_model=KnowledgeDocumentResponse)
async def get_document(doc_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(KnowledgeDocument).where(KnowledgeDocument.id == doc_id)
    result = await db.execute(stmt)
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc
