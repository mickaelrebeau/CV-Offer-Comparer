from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models.user import User
from app.services import saved_cv_service as service
from app.services.auth_service import get_current_user
from app.services.rate_limit_service import rate_limit

router = APIRouter(prefix="/cvs", tags=["saved-cvs"])

write_limit = Depends(rate_limit("saved_cvs", "DAILY_QUOTA_SAVED_CVS"))


class SavedCVIn(BaseModel):
    # Champs permissifs, validés dans le service (erreurs traduites plutôt qu'un 422 générique)
    label: str = ""
    text: str = ""
    source_filename: str | None = None
    is_default: bool = False


class SavedCVPatch(BaseModel):
    label: str | None = None
    text: str | None = None
    source_filename: str | None = None


def _listing(db: Session, user: User) -> dict:
    items = service.list_cvs(db, user)
    default = next((item for item in items if item.is_default), None)
    return {
        "items": [item.to_list_dict() for item in items],
        "default_id": str(default.id) if default else None,
        "limit": settings.MAX_SAVED_CVS,
    }


@router.get("")
def list_cvs(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """CV enregistrés (extraits uniquement, le texte complet via GET /cvs/{id})."""
    return _listing(db, user)


@router.post("", status_code=201, dependencies=[write_limit])
def create_cv(body: SavedCVIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cv = service.create(
        db,
        user,
        label=body.label,
        text=body.text,
        source_filename=body.source_filename,
        make_default=body.is_default,
    )
    return cv.to_detail_dict()


@router.get("/{cv_id}")
def get_cv(cv_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return service.get_cv(db, user, cv_id).to_detail_dict()


@router.patch("/{cv_id}", dependencies=[write_limit])
def update_cv(
    cv_id: UUID,
    body: SavedCVPatch,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cv = service.get_cv(db, user, cv_id)
    cv = service.update_cv(
        db,
        user,
        cv,
        label=body.label,
        text=body.text,
        source_filename=body.source_filename,
        replace_file="source_filename" in body.model_fields_set,
    )
    return cv.to_detail_dict()


@router.post("/{cv_id}/default")
def set_default_cv(cv_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service.set_default(db, user, service.get_cv(db, user, cv_id))
    return _listing(db, user)


@router.delete("/{cv_id}")
def delete_cv(cv_id: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service.delete(db, user, service.get_cv(db, user, cv_id))
    return _listing(db, user)
