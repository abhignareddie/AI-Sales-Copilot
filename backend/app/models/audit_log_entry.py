from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

class AuditLogEntry(Base):
    __tablename__ = "audit_log_entries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    before_state: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    after_state: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )

    user = relationship("User")
