import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, backref, mapped_column, relationship

from app.db import Base
from app.models.comparison_record import _excerpt


def letter_paragraphs(letter: dict[str, Any]) -> list[str]:
    """Paragraphes de la lettre dans l'ordre de lecture (hors objet)."""
    body = letter.get("body") or []
    parts = [letter.get("greeting"), letter.get("opening"), *body, letter.get("closing"), letter.get("signoff")]
    return [str(part) for part in parts if part]


def letter_word_count(letter: dict[str, Any]) -> int:
    return sum(len(paragraph.split()) for paragraph in letter_paragraphs(letter))


class CoverLetterRecord(Base):
    """Historique des lettres de motivation générées pour un utilisateur authentifié.

    Seuls les textes (CV, offre, lettre) sont conservés, jamais le fichier importé.
    """

    __tablename__ = "cover_letters"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    subject: Mapped[str] = mapped_column(String(320), nullable=False, default="")
    job_excerpt: Mapped[str] = mapped_column(String(320), nullable=False)
    cv_excerpt: Mapped[str] = mapped_column(String(320), nullable=False)
    tone: Mapped[str] = mapped_column(String(32), nullable=False)
    length: Mapped[str] = mapped_column(String(32), nullable=False)
    language: Mapped[str] = mapped_column(String(8), nullable=False)
    word_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    letter: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    cv_text: Mapped[str] = mapped_column(Text, nullable=False)
    # Lien de l'annonce quand l'offre a été importée depuis son URL
    offer_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    job_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Suppression du compte : la base supprime l'historique (ON DELETE CASCADE)
    user = relationship("User", backref=backref("cover_letters", cascade="all, delete-orphan", passive_deletes=True))

    @classmethod
    def from_generation(
        cls,
        *,
        user_id: uuid.UUID,
        job_text: str,
        cv_text: str,
        offer_url: str | None = None,
        tone: str,
        length: str,
        letter: dict[str, Any],
    ) -> "CoverLetterRecord":
        return cls(
            user_id=user_id,
            subject=_excerpt(letter.get("subject") or ""),
            job_excerpt=_excerpt(job_text),
            cv_excerpt=_excerpt(cv_text),
            tone=tone,
            length=length,
            language=str(letter.get("language") or "")[:8],
            word_count=letter_word_count(letter),
            letter=letter,
            cv_text=cv_text,
            offer_url=offer_url,
            job_text=job_text,
        )

    def to_list_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "subject": self.subject,
            "job_excerpt": self.job_excerpt,
            "cv_excerpt": self.cv_excerpt,
            "tone": self.tone,
            "length": self.length,
            "language": self.language,
            "word_count": self.word_count,
            "offer_url": self.offer_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def to_detail_dict(self) -> dict[str, Any]:
        return {
            **self.to_list_dict(),
            "letter": self.letter,
            "cv_text": self.cv_text,
            "job_text": self.job_text,
        }
