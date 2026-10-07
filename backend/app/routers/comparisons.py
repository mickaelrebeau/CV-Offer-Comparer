from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.db import get_db
from app.i18n import ApiError
from app.models.comparison_record import ComparisonRecord
from app.models.user import User
from app.services.auth_service import get_current_user
from app.services.comparison_diff import diff_comparisons

router = APIRouter(prefix="/comparisons", tags=["comparisons"])


def owned_comparison(db: Session, user: User, comparison_id: UUID) -> ComparisonRecord:
    """Comparaison de l'utilisateur ; 404 (et non 403) pour ne pas révéler celles des autres."""
    row = db.get(ComparisonRecord, comparison_id)
    if not row or row.user_id != user.id:
        raise ApiError(404, "history.comparison_not_found")
    return row


def _threads(db: Session, user: User) -> dict[UUID, dict]:
    """Fil de versions de chaque comparaison : racine, rang (1 = analyse initiale) et nombre de versions."""
    rows = db.execute(
        select(ComparisonRecord.id, ComparisonRecord.parent_comparison_id).where(ComparisonRecord.user_id == user.id)
    ).all()
    parents = {row.id: row.parent_comparison_id for row in rows}

    def root_and_depth(comparison_id: UUID) -> tuple[UUID, int]:
        depth, seen = 1, {comparison_id}
        while (parent := parents.get(comparison_id)) is not None and parent in parents and parent not in seen:
            comparison_id, depth = parent, depth + 1
            seen.add(parent)
        return comparison_id, depth

    info = {comparison_id: root_and_depth(comparison_id) for comparison_id in parents}
    sizes: dict[UUID, int] = {}
    for root, _ in info.values():
        sizes[root] = sizes.get(root, 0) + 1
    return {
        comparison_id: {"thread_id": str(root), "version": depth, "thread_size": sizes[root]}
        for comparison_id, (root, depth) in info.items()
    }


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

    threads = _threads(db, user)
    return {
        "items": [
            {**row.to_list_dict(), **threads.get(row.id, {"thread_id": str(row.id), "version": 1, "thread_size": 1})}
            for row in rows
        ],
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
    return owned_comparison(db, user, comparison_id).to_detail_dict()


@router.get("/{comparison_id}/diff/{other_id}")
def diff_comparison(
    comparison_id: UUID,
    other_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Évolution de `comparison_id` (avant) vers `other_id` (après)."""
    before = owned_comparison(db, user, comparison_id)
    after = owned_comparison(db, user, other_id)
    return diff_comparisons(before, after)


@router.delete("/{comparison_id}")
def delete_comparison(
    comparison_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    row = owned_comparison(db, user, comparison_id)
    # Les versions suivantes restent dans le fil : rattachées à la version précédente
    db.execute(
        update(ComparisonRecord)
        .where(ComparisonRecord.parent_comparison_id == row.id)
        .values(parent_comparison_id=row.parent_comparison_id)
    )
    db.delete(row)
    db.commit()
    return {"success": True}
