import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, backref, mapped_column, relationship

from app.db import Base

# Étapes du suivi, dans l'ordre du Kanban
APPLICATION_STATUSES = ("to_apply", "applied", "interview", "offer", "rejected")


class ApplicationRecord(Base):
    """Candidature suivie : une offre, son avancement et les analyses, lettres et entretiens associés."""

    __tablename__ = "applications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    company: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    offer_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    offer_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="to_apply")
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    # Date de la candidature : renseignée au premier passage à « Postulé » (modifiable)
    applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Suppression du compte : la base supprime les candidatures (ON DELETE CASCADE)
    user = relationship("User", backref=backref("applications", cascade="all, delete-orphan", passive_deletes=True))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "title": self.title,
            "company": self.company,
            "offer_url": self.offer_url,
            "status": self.status,
            "notes": self.notes,
            "applied_at": self.applied_at.isoformat() if self.applied_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
