from datetime import datetime, timezone
import enum

from sqlalchemy import String, DateTime, Float, Integer, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class CustomerStage(str, enum.Enum):
    PROSPECT = "prospect"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_name: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True
    )
    contact_person: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    industry: Mapped[str | None] = mapped_column(
        String(100), nullable=True, index=True
    )
    annual_revenue: Mapped[float | None] = mapped_column(Float, nullable=True)
    company_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    current_stage: Mapped[str] = mapped_column(
        SAEnum(CustomerStage), default=CustomerStage.PROSPECT, nullable=False
    )
    health_score: Mapped[float] = mapped_column(Float, default=50.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    meetings: Mapped[list["Meeting"]] = relationship(
        back_populates="customer", lazy="selectin", cascade="all, delete-orphan"
    )
    emails: Mapped[list["Email"]] = relationship(
        back_populates="customer", lazy="selectin", cascade="all, delete-orphan"
    )
    support_tickets: Mapped[list["SupportTicket"]] = relationship(
        back_populates="customer", lazy="selectin", cascade="all, delete-orphan"
    )
    recommendations: Mapped[list["Recommendation"]] = relationship(
        back_populates="customer", lazy="selectin", cascade="all, delete-orphan"
    )
    memories: Mapped[list["Memory"]] = relationship(
        back_populates="customer", lazy="selectin", cascade="all, delete-orphan"
    )
