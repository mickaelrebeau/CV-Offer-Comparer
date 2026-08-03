from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.comparison_record import ComparisonRecord
from app.models.user import User
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/comparisons", tags=["comparisons"])


@router.get("")
def list_comparisons(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    total = db.scalar(
        select(func.count())
        .select_from(ComparisonRecord)
        .where(ComparisonRecord.user_id == user.id)
    ) or 0

    rows = db.scalars(
        select(ComparisonRecord)
        .where(ComparisonRecord.user_id == user.id)
        .order_by(ComparisonRecord.created_at.desc())
        .offset(offset)
        .limit(limit)
    ).all()

    return {
        "items": [row.to_list_dict() for row in rows],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/{comparison_id}")
def get_comparison(
    comparison_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    row = db.get(ComparisonRecord, comparison_id)
    if not row or row.user_id != user.id:
        raise HTTPException(status_code=404, detail="Comparaison introuvable")
    return row.to_detail_dict()


@router.delete("/{comparison_id}")
def delete_comparison(
    comparison_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    row = db.get(ComparisonRecord, comparison_id)
    if not row or row.user_id != user.id:
        raise HTTPException(status_code=404, detail="Comparaison introuvable")
    db.delete(row)
    db.commit()
    return {"success": True}
