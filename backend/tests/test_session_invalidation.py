import re
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt
from sqlalchemy import text

from app.config import settings
from app.db import _migrate_password_changed_at, engine
from app.models.user import User
from app.services.auth_service import create_access_token, token_is_current, upsert_google_user


def _token(user: dict, *, seconds_ago: int | None = 60) -> str:
    """JWT d'une session ouverte plus tôt ; seconds_ago=None : ancien format, sans `iat`."""
    now = datetime.now(timezone.utc)
    claims = {"sub": user["user"]["id"], "email": user["email"], "exp": now + timedelta(days=1)}
    if seconds_ago is not None:
        claims["iat"] = now - timedelta(seconds=seconds_ago)
    return jwt.encode(claims, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def _me(client, token: str):
    return client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})


def _reset(client, user: dict, sent_emails, password="new-password-1"):
    client.post("/api/auth/forgot-password", json={"email": user["email"]})
    token = re.search(r"/reset-password\?token=([\w-]+)", sent_emails[-1].text).group(1)
    response = client.post("/api/auth/reset-password", json={"token": token, "password": password})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def _db_user(db_session, user: dict) -> User:
    db_session.expire_all()
    return db_session.get(User, uuid.UUID(user["user"]["id"]))


def test_access_token_carries_iat():
    token = create_access_token(str(uuid.uuid4()), "a@example.com")
    claims = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert abs(claims["iat"] - datetime.now(timezone.utc).timestamp()) < 5


def test_reset_password_revokes_existing_sessions(client, registered_user, sent_emails):
    old_session = _token(registered_user)
    assert _me(client, old_session).status_code == 200

    new_token = _reset(client, registered_user, sent_emails)

    rejected = _me(client, old_session)
    assert rejected.status_code == 401
    assert rejected.json()["code"] == "auth.session_expired"
    # Toutes les routes protégées, pas seulement /me
    assert client.get("/api/comparisons", headers={"Authorization": f"Bearer {old_session}"}).status_code == 401

    # Le jeton renvoyé par /reset-password et une nouvelle connexion restent valides
    assert _me(client, new_token).status_code == 200
    login = client.post("/api/auth/login", json={"email": registered_user["email"], "password": "new-password-1"})
    assert _me(client, login.json()["access_token"]).status_code == 200


def test_existing_sessions_survive_deployment(client, registered_user, db_session):
    # Jetons émis avant l'ajout de `iat`, compte sans changement de mot de passe
    assert _db_user(db_session, registered_user).password_changed_at is None
    assert _me(client, _token(registered_user, seconds_ago=None)).status_code == 200
    assert _me(client, registered_user["token"]).status_code == 200


def test_legacy_token_without_iat_rejected_after_reset(client, registered_user, sent_emails):
    legacy = _token(registered_user, seconds_ago=None)
    _reset(client, registered_user, sent_emails)
    assert _me(client, legacy).status_code == 401


def test_google_link_dropping_password_revokes_sessions(client, unverified_user, db_session):
    old_session = _token(unverified_user)
    user = upsert_google_user(db_session, {"sub": "g-31", "email": unverified_user["email"]})

    assert user.password_hash is None
    assert user.password_changed_at is not None
    assert _me(client, old_session).status_code == 401
    # Session ouverte par la connexion Google elle-même
    assert _me(client, create_access_token(str(user.id), user.email)).status_code == 200


def test_google_link_on_verified_account_keeps_sessions(client, registered_user, db_session):
    old_session = _token(registered_user)
    user = upsert_google_user(db_session, {"sub": "g-32", "email": registered_user["email"]})

    assert user.password_changed_at is None
    assert _me(client, old_session).status_code == 200


@pytest.mark.parametrize(
    "iat_offset,has_iat,expected",
    [
        (0, True, True),  # même seconde que le changement : jeton renvoyé par le reset
        (5, True, True),
        (-1, True, False),
        (None, False, False),
    ],
)
def test_token_is_current_boundaries(iat_offset, has_iat, expected):
    changed_at = datetime(2026, 9, 28, 12, 0, 0, tzinfo=timezone.utc)
    user = User(email="b@example.com", password_changed_at=changed_at)
    payload = {"iat": int(changed_at.timestamp()) + iat_offset} if has_iat else {}
    assert token_is_current(payload, user) is expected


def test_migration_adds_empty_column(client, registered_user, db_session):
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE users DROP COLUMN password_changed_at"))

    _migrate_password_changed_at()
    _migrate_password_changed_at()  # idempotente

    assert _db_user(db_session, registered_user).password_changed_at is None
    assert _me(client, _token(registered_user, seconds_ago=None)).status_code == 200
