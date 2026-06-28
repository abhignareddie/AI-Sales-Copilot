from datetime import datetime, timezone
import enum
from sqlalchemy import String, DateTime, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

class MemoryType(str, enum.Enum):
    CONVERSATION = "conversation"
    CUSTOMER = "customer"
    BUSINESS = "business"
    ORGANIZATIONAL = "organizational"
    KNOWLEDGE = "knowledge"
    RECOMMENDATION = "recommendation"
    REVIEWER = "reviewer"

class MemoryEntry(Base):
    __tablename__ = "memory_entries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    memory_type: Mapped[str] = mapped_column(
        SAEnum(MemoryType), default=MemoryType.CUSTOMER, nullable=False, index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    vector_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    customer = relationship("Customer", backref="memory_entries_list")
