"""Recommendation Tool — Persists AI-generated recommendations to the database."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from app.models.recommendation import Recommendation
from app.core.logging import logger


class RecommendationTool:
    """Persists recommendations to PostgreSQL."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_recommendations(
        self,
        customer_id: int,
        recommendations: list[dict],
    ) -> list[dict]:
        """Save a list of recommendations to the database."""
        saved = []
        for rec in recommendations:
            db_rec = Recommendation(
                customer_id=customer_id,
                recommendation=rec.get("action", rec.get("recommendation", "")),
                confidence=rec.get("confidence", 0.0),
                evidence=str(rec.get("evidence", "")),
                status="pending",
            )
            self.db.add(db_rec)
            await self.db.flush()
            await self.db.refresh(db_rec)
            saved.append({
                "id": db_rec.id,
                "recommendation": db_rec.recommendation,
                "confidence": db_rec.confidence,
                "status": db_rec.status,
                "created_at": db_rec.created_at.isoformat() if db_rec.created_at else None,
            })

        logger.info(f"Saved {len(saved)} recommendations for customer {customer_id}")
        return saved

    async def update_recommendation_status(
        self,
        recommendation_id: int,
        status: str,
        comment: str | None = None,
        approved_by: int | None = None,
    ) -> dict:
        """Update status of a recommendation (approve/reject/modify)."""
        from sqlalchemy import select

        result = await self.db.execute(
            select(Recommendation).where(Recommendation.id == recommendation_id)
        )
        rec = result.scalar_one_or_none()
        if not rec:
            return {"error": "Recommendation not found"}

        rec.status = status
        if approved_by:
            rec.approved_by = approved_by
        await self.db.flush()
        await self.db.refresh(rec)

        logger.info(f"Recommendation {recommendation_id} status -> {status}")
        return {
            "id": rec.id,
            "status": rec.status,
            "approved_by": rec.approved_by,
        }
