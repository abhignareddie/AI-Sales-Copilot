from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.models.memory_entry import MemoryEntry, MemoryType
from app.models.meeting import Meeting
from app.models.email import Email
from app.models.support_ticket import SupportTicket
from app.models.recommendation import Recommendation
from app.models.comment import Comment
from app.core.logging import logger

class MemoryManager:
    """Manages creation, query, and customer timeline assembly for long term memories."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_memory(self, customer_id: int, memory_type: MemoryType, content: str) -> MemoryEntry:
        """Stores a new enterprise memory entry."""
        entry = MemoryEntry(
            customer_id=customer_id,
            memory_type=memory_type,
            content=content
        )
        self.db.add(entry)
        await self.db.commit()
        await self.db.refresh(entry)
        return entry

    async def retrieve_relevant_memories(self, customer_id: int, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve memories sorted by semantic query match (simulated keyword ranking for reliability)."""
        stmt = select(MemoryEntry).where(MemoryEntry.customer_id == customer_id)
        result = await self.db.execute(stmt)
        entries = result.scalars().all()
        
        q_words = set(query.lower().split())
        scored = []
        for entry in entries:
            content_lower = entry.content.lower()
            score = 0.1
            for w in q_words:
                if w in content_lower:
                    score += 0.3
            scored.append((score, entry))
            
        scored.sort(key=lambda x: x[0], reverse=True)
        
        return [
            {
                "id": entry.id,
                "memory_type": entry.memory_type,
                "content": entry.content,
                "relevance_score": round(score, 2),
                "created_at": entry.created_at
            }
            for score, entry in scored[:limit]
        ]

    async def generate_timeline(self, customer_id: int) -> List[Dict[str, Any]]:
        """Compiles a complete chronological history of all customer contact items."""
        timeline = []
        
        # 1. Fetch Meetings
        meetings = (await self.db.execute(select(Meeting).where(Meeting.customer_id == customer_id))).scalars().all()
        for m in meetings:
            timeline.append({
                "type": "meeting",
                "title": m.title,
                "description": m.summary or "Client sync meeting",
                "timestamp": m.meeting_date,
                "meta": {"id": m.id}
            })
            
        # 2. Fetch Emails
        emails = (await self.db.execute(select(Email).where(Email.customer_id == customer_id))).scalars().all()
        for e in emails:
            timeline.append({
                "type": "email",
                "title": e.subject,
                "description": f"Email from {e.sender} to {e.receiver}",
                "timestamp": e.created_at,
                "meta": {"id": e.id}
            })
            
        # 3. Fetch Support Tickets
        tickets = (await self.db.execute(select(SupportTicket).where(SupportTicket.customer_id == customer_id))).scalars().all()
        for t in tickets:
            timeline.append({
                "type": "support_ticket",
                "title": f"Ticket #{t.ticket_number}",
                "description": f"Priority: {t.priority} | Issue: {t.issue}",
                "timestamp": t.created_at,
                "meta": {"id": t.id, "status": t.status}
            })
            
        # 4. Fetch Recommendations and Review Decisions
        recs = (await self.db.execute(select(Recommendation).where(Recommendation.customer_id == customer_id))).scalars().all()
        for r in recs:
            timeline.append({
                "type": "recommendation",
                "title": "Next Best Action Generated",
                "description": r.recommendation,
                "timestamp": r.created_at,
                "meta": {"id": r.id, "status": r.status, "confidence": r.confidence}
            })
            
        # Sort chronologically desc
        timeline.sort(key=lambda x: x["timestamp"], reverse=True)
        return timeline

class LearningEngine:
    """Implements non-retraining few-shot reinforcement using retrieved memories and approval/rejection outcomes."""
    
    @staticmethod
    def adjust_rankings(
        recommendations: List[Dict[str, Any]], 
        past_approvals: List[Dict[str, Any]], 
        past_rejections: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Adjust confidence levels of recommendations based on similarity to historical approvals/rejections."""
        approved_texts = [a.get("recommendation", "").lower() for a in past_approvals]
        rejected_texts = [r.get("recommendation", "").lower() for r in past_rejections]
        
        adjusted = []
        for rec in recommendations:
            action = rec.get("recommendation", rec.get("action", "")).lower()
            confidence = rec.get("confidence", 0.5)
            
            # Boost score if matches previously approved style
            boost = 0.0
            for app_text in approved_texts:
                if action in app_text or app_text in action:
                    boost += 0.15
                    
            # Penalize score if matches previously rejected style
            penalty = 0.0
            for rej_text in rejected_texts:
                if action in rej_text or rej_text in action:
                    penalty += 0.25
                    
            new_confidence = min(1.0, max(0.0, confidence + boost - penalty))
            rec["confidence"] = round(new_confidence, 2)
            rec["adjusted"] = boost > 0 or penalty > 0
            adjusted.append(rec)
            
        # Re-sort list based on adjusted confidence
        adjusted.sort(key=lambda x: x.get("confidence", 0.0), reverse=True)
        return adjusted
