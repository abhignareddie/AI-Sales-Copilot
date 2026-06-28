from datetime import datetime, timezone
import enum

from sqlalchemy import String, DateTime, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class TicketPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ticket_number: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )
    priority: Mapped[str] = mapped_column(
        SAEnum(TicketPriority), default=TicketPriority.MEDIUM, nullable=False
    )
    status: Mapped[str] = mapped_column(
        SAEnum(TicketStatus), default=TicketStatus.OPEN, nullable=False
    )
    issue: Mapped[str] = mapped_column(Text, nullable=False)
    resolution: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    customer: Mapped["Customer"] = relationship(back_populates="support_tickets")
