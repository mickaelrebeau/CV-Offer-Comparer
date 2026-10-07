import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, backref, mapped_column, relationship

from app.db import Base
from app.models.comparison_record import _excerpt


class CvOptimizationRecord(Base):
    """Historique de l'optimiseur de CV : propositions de reformulation pour une offre.

    Seuls les textes (CV, offre, propositions) sont conservés ; les choix accepter / rejeter
    restent côté client jusqu'à l'export ou l'enregistrement du CV optimisé.
    """

    __tablename__ = "cv_optimizations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    # Analyse d'origine (exigences manquantes ou floues ciblées), si l'optimisation part d'un résultat
    comparison_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("comparisons.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    job_excerpt: Mapped[str] = mapped_column(String(320), nullable=False)
    cv_excerpt: Mapped[str] = mapped_column(String(320), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    suggestion_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    suggestions: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    cv_text: Mapped[str] = mapped_column(Text, nullable=False)
    job_text: Mapped[str] = mapped_column(Text, nullable=False)
    offer_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Suppression du compte : la base supprime l'historique (ON DELETE CASCADE)
    user = relationship("User", backref=backref("cv_optimizations", cascade="all, delete-orphan", passive_deletes=True))

    @classmethod
    def from_result(
        cls,
        *,
        user_id: uuid.UUID,
        job_text: str,
        cv_text: str,
        offer_url: str | None = None,
        comparison_id: uuid.UUID | None = None,
        result: dict[str, Any],
    ) -> "CvOptimizationRecord":
        suggestions = result.get("suggestions") or []
        return cls(
            user_id=user_id,
            comparison_id=comparison_id,
            job_excerpt=_excerpt(job_text),
            cv_excerpt=_excerpt(cv_text),
            summary=result.get("summary") or "",
            suggestion_count=len(suggestions),
            suggestions=suggestions,
            cv_text=cv_text,
            job_text=job_text,
            offer_url=offer_url,
        )

    def to_list_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "comparison_id": str(self.comparison_id) if self.comparison_id else None,
            "job_excerpt": self.job_excerpt,
            "cv_excerpt": self.cv_excerpt,
            "summary": self.summary,
            "suggestion_count": self.suggestion_count,
            "offer_url": self.offer_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def to_detail_dict(self) -> dict[str, Any]:
        return {
            **self.to_list_dict(),
            "suggestions": self.suggestions,
            "cv_text": self.cv_text,
            "job_text": self.job_text,
        }
