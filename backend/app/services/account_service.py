import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.config import settings
from app.i18n import DEFAULT_LOCALE
from app.models.auth_token import PURPOSE_RESET_PASSWORD, PURPOSE_VERIFY_EMAIL, AuthToken
from app.models.user import User
from app.services.auth_service import get_user_by_id, hash_password
from app.services.email_service import Email, password_reset_email, verification_email


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _frontend_link(path: str, token: str, locale: str = DEFAULT_LOCALE) -> str:
    # Même langue que l'interface d'où vient la demande (/en/verify-email…)
    prefix = "" if locale == DEFAULT_LOCALE else f"/{locale}"
    return f"{settings.FRONTEND_URL.rstrip('/')}{prefix}{path}?{urlencode({'token': token})}"


def issue_token(db: Session, user: User, purpose: str, ttl: timedelta) -> str:
    """Crée un jeton à usage unique ; les jetons précédents de même usage sont révoqués."""
    db.execute(delete(AuthToken).where(AuthToken.user_id == user.id, AuthToken.purpose == purpose))
    token = secrets.token_urlsafe(32)
    db.add(
        AuthToken(
            user_id=user.id,
            purpose=purpose,
            token_hash=_hash(token),
            expires_at=datetime.now(timezone.utc) + ttl,
        )
    )
    db.commit()
    return token


def consume_token(db: Session, token: str, purpose: str) -> User | None:
    """Valide et supprime le jeton (usage unique). Renvoie l'utilisateur, ou None si invalide/expiré."""
    record = db.scalar(
        select(AuthToken).where(AuthToken.token_hash == _hash(token), AuthToken.purpose == purpose)
    )
    if not record:
        return None
    db.delete(record)
    db.commit()
    if record.expires_at < datetime.now(timezone.utc):
        return None
    return get_user_by_id(db, record.user_id)


def build_verification_email(db: Session, user: User, locale: str = DEFAULT_LOCALE) -> Email:
    token = issue_token(
        db, user, PURPOSE_VERIFY_EMAIL, timedelta(hours=settings.EMAIL_VERIFICATION_TTL_HOURS)
    )
    return verification_email(user.email, _frontend_link("/verify-email", token, locale), locale)


def build_password_reset_email(db: Session, user: User, locale: str = DEFAULT_LOCALE) -> Email:
    token = issue_token(
        db, user, PURPOSE_RESET_PASSWORD, timedelta(minutes=settings.PASSWORD_RESET_TTL_MINUTES)
    )
    return password_reset_email(user.email, _frontend_link("/reset-password", token, locale), locale)


def mark_email_verified(db: Session, user: User) -> User:
    if not user.email_verified_at:
        user.email_verified_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(user)
    return user


def reset_password(db: Session, user: User, password: str) -> User:
    user.password_hash = hash_password(password)
    # Déconnecte les sessions ouvertes avec l'ancien mot de passe (le JWT renvoyé reste valide)
    user.mark_password_changed()
    # Le lien a été reçu sur la boîte mail : l'adresse est prouvée
    user.email_verified_at = user.email_verified_at or datetime.now(timezone.utc)
    db.execute(
        delete(AuthToken).where(AuthToken.user_id == user.id, AuthToken.purpose == PURPOSE_RESET_PASSWORD)
    )
    db.commit()
    db.refresh(user)
    return user
