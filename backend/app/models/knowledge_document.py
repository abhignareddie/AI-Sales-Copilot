from datetime import datetime, timezone
import enum

from sqlalchemy import String, DateTime, ForeignKey, Enum as SAEnum, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class DocumentType(str, enum.Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    CSV = "csv"
    MD = "md"
    HTML = "html"


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    document_type: Mapped[str] = mapped_column(
        SAEnum(DocumentType), nullable=False
    )
    uploaded_file: Mapped[str] = mapped_column(String(500), nullable=False)
    uploaded_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    file_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    uploader: Mapped["User"] = relationship(back_populates="knowledge_documents")

