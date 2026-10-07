from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.i18n import ApiError, request_locale
from app.models.cv_optimization_record import CvOptimizationRecord
from app.models.user import User
from app.routers.compare import _sse_headers
from app.routers.comparisons import owned_comparison
from app.routers.cover_letters import MAX_TEXT_CHARS
from app.services.auth_service import get_current_user, require_verified_user
from app.services.cv_optimizer_service import stream_cv_optimization
from app.services.job_offers.service import safe_offer_url
from app.services.llm_credentials_service import ai_for_user
from app.services.rate_limit_service import rate_limit

router = APIRouter(tags=["cv-optimizer"])


class CvOptimizationRequest(BaseModel):
    # À partir d'une analyse : son CV, son offre et ses exigences manquantes ou floues
    comparison_id: Optional[UUID] = None
    # Sinon : CV et offre du contexte courant
    cv_text: str = ""
    job_text: str = ""
    offer_url: Optional[str] = None


def _gaps(items: list) -> list[dict[str, str]]:
    """Exigences manquantes puis floues de l'analyse, cibles prioritaires des reformulations."""
    gaps = [
        {"status": str(item.get("status")), "category": str(item.get("category") or ""), "offerText": str(item.get("offerText") or "")}
        for item in items or []
        if isinstance(item, dict) and item.get("status") in ("missing", "unclear")
    ]
    return sorted(gaps, key=lambda gap: gap["status"] != "missing")


@router.post(
    "/cv-optimizer",
    dependencies=[
        Depends(require_verified_user),
        Depends(rate_limit("cv_optimizer", "DAILY_QUOTA_CV_OPTIMIZER")),
    ],
)
async def optimize_cv(
    request: CvOptimizationRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    locale: str = Depends(request_locale),
):
    """Propose des reformulations ciblées du CV pour l'offre (flux SSE) et les enregistre dans l'historique."""
    if request.comparison_id is not None:
        comparison = owned_comparison(db, user, request.comparison_id)
        cv, job, offer_url = comparison.cv_text.strip(), comparison.offer_text.strip(), comparison.offer_url
        gaps = _gaps(comparison.items)
    else:
        cv, job, offer_url = request.cv_text.strip(), request.job_text.strip(), safe_offer_url(request.offer_url)
        gaps = []

    if not job:
        raise ApiError(400, "interview.job_empty")
    if not cv:
        raise ApiError(400, "cover_letter.cv_missing")
    if len(job) > MAX_TEXT_CHARS or len(cv) > MAX_TEXT_CHARS:
        raise ApiError(413, "cover_letter.text_too_long", max_chars=MAX_TEXT_CHARS)

    ai = ai_for_user(db, user)

    def persist(result) -> str:
        record = CvOptimizationRecord.from_result(
            user_id=user.id,
            job_text=job,
            cv_text=cv,
            offer_url=offer_url,
            comparison_id=request.comparison_id,
            result=result,
        )
        db.add(record)
        db.commit()
        return str(record.id)

    return StreamingResponse(
        stream_cv_optimization(cv, job, gaps=gaps, locale=locale, on_result=persist, ai=ai),
        media_type="text/event-stream",
        headers=_sse_headers(),
    )


def _owned(db: Session, user: User, optimization_id: UUID) -> CvOptimizationRecord:
    row = db.get(CvOptimizationRecord, optimization_id)
    if not row or row.user_id != user.id:
        raise ApiError(404, "history.cv_optimization_not_found")
    return row


@router.get("/cv-optimizations")
def list_cv_optimizations(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    total = db.scalar(
        select(func.count())
        .select_from(CvOptimizationRecord)
        .where(CvOptimizationRecord.user_id == user.id)
    ) or 0

    rows = db.scalars(
        select(CvOptimizationRecord)
        .where(CvOptimizationRecord.user_id == user.id)
        .order_by(CvOptimizationRecord.created_at.desc())
        .offset(offset)
        .limit(limit)
    ).all()

    return {
        "items": [row.to_list_dict() for row in rows],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/cv-optimizations/{optimization_id}")
def get_cv_optimization(
    optimization_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _owned(db, user, optimization_id).to_detail_dict()


@router.delete("/cv-optimizations/{optimization_id}")
def delete_cv_optimization(
    optimization_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db.delete(_owned(db, user, optimization_id))
    db.commit()
    return {"success": True}
