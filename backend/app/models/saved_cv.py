import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, backref, mapped_column, relationship

from app.db import Base
from app.models.comparison_record import _excerpt


class SavedCV(Base):
    """CV enregistré par un utilisateur pour être réutilisé dans tous les modules.

    Seul le texte extrait est conservé, jamais le fichier importé (PDF / TXT).
    """

    __tablename__ = "saved_cvs"
    __table_args__ = (
        # Garantie en base : au plus un CV par défaut par utilisateur
        Index("uq_saved_cvs_default", "user_id", unique=True, postgresql_where=text("is_default")),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    label: Mapped[str] = mapped_column(String(80), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    source_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Suppression du compte : la base purge les CV (ON DELETE CASCADE)
    user = relationship("User", backref=backref("saved_cvs", cascade="all, delete-orphan", passive_deletes=True))

    def to_list_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "label": self.label,
            "source_filename": self.source_filename,
            "is_default": self.is_default,
            "char_count": len(self.text),
            "excerpt": _excerpt(self.text),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def to_detail_dict(self) -> dict[str, Any]:
        return {**self.to_list_dict(), "text": self.text}
