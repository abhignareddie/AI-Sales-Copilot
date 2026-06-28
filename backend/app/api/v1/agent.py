"""Agent API Routes — Agent execution, knowledge, memory, and graph endpoints."""

from __future__ import annotations

import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user
from app.agents.graph.graph_executor import GraphExecutor
from app.agents.tools.knowledge_tool import KnowledgeTool
from app.agents.tools.memory_tool import MemoryTool
from app.agents.tools.recommendation_tool import RecommendationTool
from app.models.user import User
from app.core.logging import logger

router = APIRouter()


# ─── Request/Response Schemas ─────────────────────────────

class AgentRunRequest(BaseModel):
    customer_id: int = Field(..., description="Customer ID to analyze")
    business_goal: str = Field(
        default="Generate next best actions to advance this deal",
        description="Business objective for the analysis",
    )


class AgentExplainRequest(BaseModel):
    customer_id: int
    recommendation_index: int = Field(default=0, description="Index of recommendation to explain")
    business_goal: str = Field(default="Explain this recommendation in detail")


class ReviewRequest(BaseModel):
    recommendation_id: int
    action: str = Field(..., description="approve, reject, or modify")
    comment: Optional[str] = None


class KnowledgeIngestRequest(BaseModel):
    file_path: str = Field(..., description="Path to document file")
    title: str = Field(default="", description="Document title")
    document_type: str = Field(default="general", description="Document category")


class KnowledgeSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query")
    top_k: int = Field(default=5, ge=1, le=20)
    document_type: Optional[str] = None


class MemorySearchRequest(BaseModel):
    customer_id: int
    memory_type: Optional[str] = None
    limit: int = Field(default=20, ge=1, le=100)


# ─── Agent Execution ─────────────────────────────────────

@router.post("/agent/run")
async def run_agent_pipeline(
    request: AgentRunRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Execute the full multi-agent pipeline for a customer."""
    logger.info(
        f"[api] Agent run: customer={request.customer_id}, "
        f"user={current_user.id}, goal='{request.business_goal[:50]}'"
    )

    executor = GraphExecutor(db)
    result = await executor.execute(
        customer_id=request.customer_id,
        business_goal=request.business_goal,
        user_id=current_user.id,
    )
    return result


@router.post("/agent/run/stream")
async def run_agent_pipeline_stream(
    request: AgentRunRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Execute the pipeline with Server-Sent Events streaming."""
    executor = GraphExecutor(db)

    async def event_generator():
        async for event in executor.execute_streaming(
            customer_id=request.customer_id,
            business_goal=request.business_goal,
            user_id=current_user.id,
        ):
            yield f"data: {json.dumps(event, default=str)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.post("/agent/explain")
async def explain_recommendation(
    request: AgentExplainRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get detailed explanation for a specific recommendation."""
    executor = GraphExecutor(db)
    result = await executor.execute(
        customer_id=request.customer_id,
        business_goal=request.business_goal,
        user_id=current_user.id,
    )

    recommendations = result.get("recommendations", [])
    if not recommendations:
        raise HTTPException(status_code=404, detail="No recommendations generated")

    idx = min(request.recommendation_index, len(recommendations) - 1)
    rec = recommendations[idx]

    return {
        "recommendation": rec,
        "customer_summary": result.get("customer_summary", {}),
        "risk_context": result.get("risk", {}),
        "opportunity_context": result.get("opportunity", {}),
        "evidence": result.get("evidence", []),
        "retrieved_documents": result.get("retrieved_documents", []),
        "planner_reasoning": result.get("planner_reasoning", ""),
        "overall_confidence": result.get("confidence", 0),
    }


# ─── Human Review ────────────────────────────────────────

@router.post("/agent/review")
async def submit_review(
    request: ReviewRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit a human review decision for a recommendation."""
    valid_actions = {"approve", "reject", "modify"}
    if request.action not in valid_actions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid action. Must be one of: {valid_actions}",
        )

    tool = RecommendationTool(db)
    result = await tool.update_recommendation_status(
        recommendation_id=request.recommendation_id,
        status=request.action + "d",  # approved, rejected, modified
        comment=request.comment,
        approved_by=current_user.id,
    )

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return {"success": True, "result": result}


# ─── Knowledge Base ──────────────────────────────────────

@router.post("/knowledge/ingest")
async def ingest_knowledge_document(
    request: KnowledgeIngestRequest,
    current_user: User = Depends(get_current_user),
):
    """Ingest a document into the ChromaDB knowledge base."""
    try:
        tool = KnowledgeTool()
        result = tool.ingest_knowledge_document(
            file_path=request.file_path,
            title=request.title,
            document_type=request.document_type,
        )
        return {"success": True, "result": result}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@router.post("/knowledge/search")
async def search_knowledge_base(
    request: KnowledgeSearchRequest,
    current_user: User = Depends(get_current_user),
):
    """Search the enterprise knowledge base."""
    try:
        tool = KnowledgeTool()
        results = tool.search_knowledge(
            query=request.query,
            top_k=request.top_k,
            document_type=request.document_type,
        )
        return {"query": request.query, "results": results, "total": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


# ─── Memory ──────────────────────────────────────────────

@router.post("/memory/search")
async def search_customer_memory(
    request: MemorySearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Search customer long-term memory."""
    tool = MemoryTool(db)
    memories = await tool.retrieve_memory(
        customer_id=request.customer_id,
        memory_type=request.memory_type,
        limit=request.limit,
    )
    return {"customer_id": request.customer_id, "memories": memories, "total": len(memories)}


# ─── Graph Status ────────────────────────────────────────

@router.get("/graph/status")
async def get_graph_status(current_user: User = Depends(get_current_user)):
    """Get the graph configuration and health status."""
    from app.core.config import settings

    return {
        "status": "operational",
        "graph_nodes": [
            "planner", "crm", "knowledge", "transcript", "email",
            "support", "risk", "opportunity", "recommendation",
            "human_review", "memory",
        ],
        "parallel_groups": [
            {"step": 2, "agents": ["knowledge", "transcript", "email", "support"]},
        ],
        "config": {
            "llm_model": settings.OPENAI_MODEL,
            "embedding_model": settings.EMBEDDING_MODEL,
            "rag_top_k": settings.RAG_TOP_K,
            "max_retries": settings.AGENT_MAX_RETRIES,
            "has_openai_key": bool(settings.OPENAI_API_KEY),
            "has_gemini_key": bool(settings.GEMINI_API_KEY),
            "chroma_collection": settings.CHROMA_COLLECTION,
        },
    }
