import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.comparison_record import _excerpt


class InterviewRecord(Base):
    """Historique des simulations d'entretien pour un utilisateur authentifié."""

    __tablename__ = "interviews"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    job_excerpt: Mapped[str] = mapped_column(String(320), nullable=False)
    cv_excerpt: Mapped[str] = mapped_column(String(320), nullable=False)
    score_global: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    num_questions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    questions: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    answers: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    analysis: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    cv_text: Mapped[str] = mapped_column(Text, nullable=False)
    job_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user = relationship("User", backref="interviews")

    @classmethod
    def from_session(
        cls,
        *,
        user_id: uuid.UUID,
        job_text: str,
        cv_text: str,
        questions: list[Any],
        answers: list[Any],
        analysis: dict[str, Any],
        duration_seconds: int = 0,
    ) -> "InterviewRecord":
        raw_score = analysis.get("score_global") or 0
        try:
            score = float(raw_score)
        except (TypeError, ValueError):
            score = 0.0

        return cls(
            user_id=user_id,
            job_excerpt=_excerpt(job_text),
            cv_excerpt=_excerpt(cv_text),
            score_global=score,
            num_questions=len(questions),
            duration_seconds=max(0, int(duration_seconds or 0)),
            questions=questions,
            answers=answers,
            analysis=analysis,
            cv_text=cv_text,
            job_text=job_text,
        )

    def to_list_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "job_excerpt": self.job_excerpt,
            "cv_excerpt": self.cv_excerpt,
            "score_global": self.score_global,
            "num_questions": self.num_questions,
            "duration_seconds": self.duration_seconds,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def to_detail_dict(self) -> dict[str, Any]:
        return {
            **self.to_list_dict(),
            "questions": self.questions,
            "answers": self.answers,
            "analysis": self.analysis,
            "cv_text": self.cv_text,
            "job_text": self.job_text,
        }
