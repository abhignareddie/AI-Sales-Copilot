from datetime import datetime, timezone
import enum

from sqlalchemy import String, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    SALES_REP = "sales_rep"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        SAEnum(UserRole), default=UserRole.SALES_REP, nullable=False
    )
    avatar: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    mfa_enabled: Mapped[bool] = mapped_column(default=False, nullable=False)
    otp_secret: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Relationships
    audit_logs: Mapped[list["AuditLog"]] = relationship(
        back_populates="user", lazy="selectin"
    )
    knowledge_documents: Mapped[list["KnowledgeDocument"]] = relationship(
        back_populates="uploader", lazy="selectin"
    )
