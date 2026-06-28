from datetime import datetime, timezone
import enum

from sqlalchemy import String, DateTime, Text, Float, ForeignKey, Integer, Enum as SAEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class RecommendationStatus(str, enum.Enum):
    SUPPORT = "Support"
    DRAFT = "Draft"
    PENDING_REVIEW = "Pending Review"
    UNDER_REVIEW = "Under Review"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    MODIFIED = "Modified"
    ESCALATED = "Escalated"
    EXECUTED = "Executed"
    CLOSED = "Closed"
    CANCELLED = "Cancelled"



class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    evidence: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        SAEnum(RecommendationStatus),
        default=RecommendationStatus.PENDING_REVIEW,
        nullable=False,
    )
    approved_by: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reviewer_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    feedback: Mapped[str | None] = mapped_column(String(100), nullable=True)
    details: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    customer: Mapped["Customer"] = relationship(back_populates="recommendations")

