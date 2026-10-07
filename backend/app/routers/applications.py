from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.i18n import ApiError
from app.models.application_record import APPLICATION_STATUSES, ApplicationRecord
from app.models.comparison_record import ComparisonRecord
from app.models.cover_letter_record import CoverLetterRecord
from app.models.interview_record import InterviewRecord
from app.models.user import User
from app.routers.comparisons import owned_comparison
from app.services.auth_service import get_current_user
from app.services.job_offers.service import safe_offer_url
from app.services.rate_limit_service import rate_limit

router = APIRouter(prefix="/applications", tags=["applications"])

MAX_OFFER_CHARS = 50_000
# Étapes à partir desquelles la candidature est envoyée (date de candidature renseignée)
SENT_STATUSES = ("applied", "interview", "offer", "rejected")


class ApplicationCreate(BaseModel):
    title: str = Field(default="", max_length=200)
    company: str = Field(default="", max_length=200)
    offer_url: Optional[str] = None
    offer_text: str = Field(default="", max_length=MAX_OFFER_CHARS)
    status: str = "to_apply"
    notes: str = Field(default="", max_length=10_000)
    # « Suivre cette candidature » après une analyse : offre reprise et analyse rattachée
    comparison_id: Optional[UUID] = None


class ApplicationUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=200)
    company: Optional[str] = Field(default=None, max_length=200)
    offer_url: Optional[str] = None
    offer_text: Optional[str] = Field(default=None, max_length=MAX_OFFER_CHARS)
    status: Optional[str] = None
    notes: Optional[str] = Field(default=None, max_length=10_000)


def owned_application(db: Session, user: User, application_id: UUID) -> ApplicationRecord:
    """Candidature de l'utilisateur ; 404 pour ne pas révéler celles des autres."""
    row = db.get(ApplicationRecord, application_id)
    if not row or row.user_id != user.id:
        raise ApiError(404, "application.not_found")
    return row


def linked_application_id(db: Session, user: User, application_id: UUID | str | None) -> UUID | None:
    """Rattachement d'une analyse, lettre ou simulation à une candidature (appartenance vérifiée)."""
    if not application_id:
        return None
    try:
        parsed = application_id if isinstance(application_id, UUID) else UUID(str(application_id))
    except ValueError as exc:
        raise ApiError(404, "application.not_found") from exc
    return owned_application(db, user, parsed).id


def _title_from_offer(offer_text: str) -> str:
    """Intitulé par défaut : première ligne non vide de l'offre."""
    first_line = next((line.strip() for line in offer_text.splitlines() if line.strip()), "")
    return first_line[:200]


def _check_status(status: str) -> None:
    if status not in APPLICATION_STATUSES:
        raise ApiError(400, "application.invalid_status")


def _mark_sent(row: ApplicationRecord) -> None:
    if row.status in SENT_STATUSES and row.applied_at is None:
        row.applied_at = datetime.now(timezone.utc)


def _stats(db: Session, application_ids: list[UUID]) -> dict[UUID, dict]:
    """Nombre d'analyses, lettres et simulations rattachées, et dernier score d'analyse."""
    stats = {
        application_id: {"comparison_count": 0, "interview_count": 0, "cover_letter_count": 0, "last_score": None}
        for application_id in application_ids
    }
    if not application_ids:
        return stats
    for model, key in (
        (ComparisonRecord, "comparison_count"),
        (InterviewRecord, "interview_count"),
        (CoverLetterRecord, "cover_letter_count"),
    ):
        rows = db.execute(
            select(model.application_id, func.count())
            .where(model.application_id.in_(application_ids))
            .group_by(model.application_id)
        ).all()
        for application_id, count in rows:
            stats[application_id][key] = count
    latest = db.execute(
        select(ComparisonRecord.application_id, ComparisonRecord.match_percentage)
        .where(ComparisonRecord.application_id.in_(application_ids))
        .distinct(ComparisonRecord.application_id)
        .order_by(ComparisonRecord.application_id, ComparisonRecord.created_at.desc())
    ).all()
    for application_id, score in latest:
        stats[application_id]["last_score"] = score
    return stats


def _detail(db: Session, row: ApplicationRecord) -> dict:
    def linked(model, fields):
        records = db.scalars(
            select(model).where(model.application_id == row.id).order_by(model.created_at.desc())
        ).all()
        return [
            {
                "id": str(record.id),
                "created_at": record.created_at.isoformat() if record.created_at else None,
                **{field: getattr(record, field) for field in fields},
            }
            for record in records
        ]

    return {
        **row.to_dict(),
        **_stats(db, [row.id])[row.id],
        "offer_text": row.offer_text,
        "comparisons": linked(ComparisonRecord, ("match_percentage", "matches", "total_items")),
        "interviews": linked(InterviewRecord, ("score_global", "num_questions")),
        "cover_letters": linked(CoverLetterRecord, ("subject", "word_count")),
    }


@router.get("")
def list_applications(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.scalars(
        select(ApplicationRecord)
        .where(ApplicationRecord.user_id == user.id)
        .order_by(ApplicationRecord.updated_at.desc())
    ).all()
    stats = _stats(db, [row.id for row in rows])
    return {"items": [{**row.to_dict(), **stats[row.id]} for row in rows], "total": len(rows)}


@router.post("", dependencies=[Depends(rate_limit("applications", "DAILY_QUOTA_APPLICATIONS"))])
def create_application(
    body: ApplicationCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _check_status(body.status)
    comparison = owned_comparison(db, user, body.comparison_id) if body.comparison_id else None
    offer_text = body.offer_text.strip() or (comparison.offer_text if comparison else "")
    offer_url = safe_offer_url(body.offer_url) or (comparison.offer_url if comparison else None)
    title = body.title.strip() or _title_from_offer(offer_text)
    if not title:
        raise ApiError(400, "application.title_missing")

    row = ApplicationRecord(
        user_id=user.id,
        title=title,
        company=body.company.strip(),
        offer_url=offer_url,
        offer_text=offer_text,
        status=body.status,
        notes=body.notes.strip(),
    )
    _mark_sent(row)
    db.add(row)
    db.flush()
    if comparison is not None:
        comparison.application_id = row.id
    db.commit()
    db.refresh(row)
    return _detail(db, row)


@router.get("/{application_id}")
def get_application(
    application_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _detail(db, owned_application(db, user, application_id))


@router.patch("/{application_id}")
def update_application(
    application_id: UUID,
    body: ApplicationUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    row = owned_application(db, user, application_id)
    changes = body.model_dump(exclude_unset=True)
    if "status" in changes:
        _check_status(changes["status"] or "")
    if "title" in changes:
        changes["title"] = (changes["title"] or "").strip()
        if not changes["title"]:
            raise ApiError(400, "application.title_missing")
    if "offer_url" in changes:
        changes["offer_url"] = safe_offer_url(changes["offer_url"])
    for field in ("company", "notes", "offer_text"):
        if field in changes:
            changes[field] = (changes[field] or "").strip()

    for field, value in changes.items():
        setattr(row, field, value)
    _mark_sent(row)
    db.commit()
    db.refresh(row)
    return _detail(db, row)


@router.delete("/{application_id}")
def delete_application(
    application_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Les analyses, lettres et simulations rattachées sont conservées (ON DELETE SET NULL)
    db.delete(owned_application(db, user, application_id))
    db.commit()
    return {"success": True}
