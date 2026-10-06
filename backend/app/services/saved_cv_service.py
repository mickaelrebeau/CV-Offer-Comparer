"""Bibliothèque de CV enregistrés : un utilisateur réutilise ses CV dans tous les modules."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.config import settings
from app.i18n import ApiError
from app.models.saved_cv import SavedCV
from app.models.user import User

MAX_LABEL_LENGTH = 80
MAX_FILENAME_LENGTH = 255
# Même limite que les textes de CV acceptés par les autres modules (lettre de motivation)
MAX_CV_TEXT_CHARS = 50_000


def _lock_user(db: Session, user: User) -> None:
    """Sérialise les écritures d'un même utilisateur (limite et CV par défaut sans course)."""
    db.execute(select(User.id).where(User.id == user.id).with_for_update())


def _clean_label(label: str | None) -> str:
    label = " ".join((label or "").split())
    if not label or len(label) > MAX_LABEL_LENGTH:
        raise ApiError(400, "cvs.invalid_label", max_chars=MAX_LABEL_LENGTH)
    return label


def _clean_text(value: str | None) -> str:
    value = (value or "").strip()
    if not value:
        raise ApiError(400, "cvs.empty_text")
    if len(value) > MAX_CV_TEXT_CHARS:
        raise ApiError(413, "cvs.text_too_long", max_chars=MAX_CV_TEXT_CHARS)
    return value


def _clean_filename(filename: str | None) -> str | None:
    filename = (filename or "").strip()
    # Nom affiché uniquement : on retire un éventuel chemin et on tronque
    filename = filename.replace("\\", "/").rsplit("/", 1)[-1]
    return filename[:MAX_FILENAME_LENGTH] or None


def list_cvs(db: Session, user: User) -> list[SavedCV]:
    return list(
        db.scalars(
            select(SavedCV)
            .where(SavedCV.user_id == user.id)
            .order_by(SavedCV.is_default.desc(), SavedCV.updated_at.desc())
        )
    )


def get_cv(db: Session, user: User, cv_id: uuid.UUID) -> SavedCV:
    cv = db.get(SavedCV, cv_id)
    # Même réponse qu'un id inexistant : l'existence d'un CV d'un autre compte n'est pas révélée
    if not cv or cv.user_id != user.id:
        raise ApiError(404, "cvs.not_found")
    return cv


def _clear_default(db: Session, user: User) -> None:
    db.execute(
        update(SavedCV)
        .where(SavedCV.user_id == user.id, SavedCV.is_default.is_(True))
        .values(is_default=False)
    )
    # Avant de définir le nouveau défaut : l'index unique partiel n'admet qu'une ligne
    db.flush()


def create(
    db: Session,
    user: User,
    *,
    label: str | None,
    text: str | None,
    source_filename: str | None,
    make_default: bool,
) -> SavedCV:
    label = _clean_label(label)
    text = _clean_text(text)
    _lock_user(db, user)

    count = db.scalar(select(func.count()).select_from(SavedCV).where(SavedCV.user_id == user.id)) or 0
    if count >= settings.MAX_SAVED_CVS:
        raise ApiError(409, "cvs.limit_reached", max=settings.MAX_SAVED_CVS)

    cv = SavedCV(
        user_id=user.id,
        label=label,
        text=text,
        source_filename=_clean_filename(source_filename),
    )
    # Premier CV : défini par défaut d'office
    if make_default or count == 0:
        _clear_default(db, user)
        cv.is_default = True
    db.add(cv)
    db.commit()
    db.refresh(cv)
    return cv


def update_cv(
    db: Session,
    user: User,
    cv: SavedCV,
    *,
    label: str | None = None,
    text: str | None = None,
    source_filename: str | None = None,
    replace_file: bool = False,
) -> SavedCV:
    """Renommer (`label`) et/ou remplacer le contenu (`text`, nouveau `source_filename`)."""
    if label is not None:
        cv.label = _clean_label(label)
    if text is not None:
        cv.text = _clean_text(text)
        cv.source_filename = _clean_filename(source_filename)
    elif replace_file:
        cv.source_filename = _clean_filename(source_filename)
    db.commit()
    db.refresh(cv)
    return cv


def set_default(db: Session, user: User, cv: SavedCV) -> SavedCV:
    _lock_user(db, user)
    _clear_default(db, user)
    cv.is_default = True
    db.commit()
    db.refresh(cv)
    return cv


def delete(db: Session, user: User, cv: SavedCV) -> None:
    _lock_user(db, user)
    was_default = cv.is_default
    db.delete(cv)
    db.flush()
    # Le CV par défaut supprimé : le plus récemment modifié prend le relais
    if was_default:
        successor = db.scalar(
            select(SavedCV).where(SavedCV.user_id == user.id).order_by(SavedCV.updated_at.desc()).limit(1)
        )
        if successor:
            successor.is_default = True
    db.commit()
