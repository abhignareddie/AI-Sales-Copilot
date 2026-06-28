from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Text, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref
from app.database.base import Base

class Comment(Base):
    __tablename__ = "recommendation_comments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    recommendation_id: Mapped[int] = mapped_column(
        ForeignKey("recommendations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("recommendation_comments.id", ondelete="CASCADE"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    recommendation = relationship("Recommendation", backref="comments_list")
    user = relationship("User")
    replies = relationship("Comment", backref=backref("parent", remote_side=[id]))
