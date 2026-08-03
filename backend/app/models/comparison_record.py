import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def _excerpt(text: str, limit: int = 280) -> str:
    cleaned = " ".join((text or "").split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1].rstrip() + "…"


class ComparisonRecord(Base):
    """Historique des analyses CV ↔ offre pour un utilisateur authentifié."""

    __tablename__ = "comparisons"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    offer_excerpt: Mapped[str] = mapped_column(String(320), nullable=False)
    cv_excerpt: Mapped[str] = mapped_column(String(320), nullable=False)
    match_percentage: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_items: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    matches: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    missing: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    unclear: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    summary: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    items: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    offer_text: Mapped[str] = mapped_column(Text, nullable=False)
    cv_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user = relationship("User", backref="comparisons")

    @classmethod
    def from_analysis(
        cls,
        *,
        user_id: uuid.UUID,
        offer_text: str,
        cv_text: str,
        items: list[Any],
        summary: dict[str, Any],
    ) -> "ComparisonRecord":
        return cls(
            user_id=user_id,
            offer_excerpt=_excerpt(offer_text),
            cv_excerpt=_excerpt(cv_text),
            match_percentage=float(summary.get("matchPercentage") or 0),
            total_items=int(summary.get("totalItems") or len(items)),
            matches=int(summary.get("matches") or 0),
            missing=int(summary.get("missing") or 0),
            unclear=int(summary.get("unclear") or 0),
            summary=summary,
            items=items,
            offer_text=offer_text,
            cv_text=cv_text,
        )

    def to_list_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "offer_excerpt": self.offer_excerpt,
            "cv_excerpt": self.cv_excerpt,
            "match_percentage": self.match_percentage,
            "total_items": self.total_items,
            "matches": self.matches,
            "missing": self.missing,
            "unclear": self.unclear,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def to_detail_dict(self) -> dict[str, Any]:
        return {
            **self.to_list_dict(),
            "summary": self.summary,
            "items": self.items,
            "offer_text": self.offer_text,
            "cv_text": self.cv_text,
        }
