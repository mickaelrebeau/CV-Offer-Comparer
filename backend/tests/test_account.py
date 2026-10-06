import re
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import text

from app.db import engine
from app.migrations import upgrade_legacy_schema
from app.models.auth_token import AuthToken
from app.models.comparison_record import ComparisonRecord
from app.models.interview_record import InterviewRecord
from app.models.user import User
from app.services.auth_service import upsert_google_user


def _token_from(email, path: str) -> str:
    match = re.search(rf"{path}\?token=([\w-]+)", email.text)
    assert match, email.text
    return match.group(1)


def _headers(user) -> dict:
    return {"Authorization": f"Bearer {user['token']}"}


# --- Vérification d'e-mail ----------------------------------------------------


def test_register_sends_verification_email(unverified_user, sent_emails):
    assert unverified_user["user"]["email_verified"] is False
    assert len(sent_emails) == 1
    assert sent_emails[0].to == unverified_user["email"]
    assert _token_from(sent_emails[0], "/verify-email")


def test_verify_email_is_single_use(client, unverified_user, sent_emails):
    token = _token_from(sent_emails[0], "/verify-email")

    response = client.post("/api/auth/verify-email", json={"token": token})
    assert response.status_code == 200
    assert response.json()["email_verified"] is True
    assert client.get("/api/auth/me", headers=_headers(unverified_user)).json()["email_verified"] is True

    assert client.post("/api/auth/verify-email", json={"token": token}).status_code == 400


def test_verify_email_rejects_unknown_and_expired_tokens(client, unverified_user, sent_emails, db_session):
    assert client.post("/api/auth/verify-email", json={"token": "nope"}).status_code == 400

    token = _token_from(sent_emails[0], "/verify-email")
    record = db_session.query(AuthToken).one()
    record.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    db_session.commit()
    assert client.post("/api/auth/verify-email", json={"token": token}).status_code == 400


def test_resend_verification_revokes_previous_link(client, unverified_user, sent_emails):
    old_token = _token_from(sent_emails[0], "/verify-email")
    response = client.post("/api/auth/resend-verification", headers=_headers(unverified_user))
    assert response.status_code == 200
    new_token = _token_from(sent_emails[1], "/verify-email")

    assert client.post("/api/auth/verify-email", json={"token": old_token}).status_code == 400
    assert client.post("/api/auth/verify-email", json={"token": new_token}).status_code == 200


def test_resend_verification_requires_auth(client):
    assert client.post("/api/auth/resend-verification").status_code in (401, 403)


# --- Politique des comptes non vérifiés -----------------------------------------


@pytest.mark.parametrize(
    "path",
    ["/api/compare-stream", "/api/interview/generate-questions", "/api/interview/analyze-responses"],
)
def test_unverified_user_cannot_use_ai_routes(client, unverified_user, path):
    response = client.post(path, headers=_headers(unverified_user))
    assert response.status_code == 403
    assert "Confirmez votre adresse" in response.json()["detail"]


def test_verified_user_passes_verification_check(client, registered_user):
    response = client.post("/api/compare-stream", headers=_headers(registered_user))
    assert response.status_code == 422  # corps manquant : la vérification e-mail est passée


def test_unverified_user_keeps_access_to_account(client, unverified_user):
    assert client.get("/api/auth/me", headers=_headers(unverified_user)).status_code == 200
    assert client.get("/api/comparisons", headers=_headers(unverified_user)).status_code == 200


# --- Mot de passe oublié ------------------------------------------------------


def test_forgot_password_does_not_reveal_accounts(client, registered_user, sent_emails):
    sent_emails.clear()
    known = client.post("/api/auth/forgot-password", json={"email": registered_user["email"]})
    unknown = client.post("/api/auth/forgot-password", json={"email": "ghost@example.com"})

    assert known.status_code == unknown.status_code == 200
    assert known.json() == unknown.json()
    assert [email.to for email in sent_emails] == [registered_user["email"]]


def test_reset_password_flow(client, unverified_user, sent_emails):
    client.post("/api/auth/forgot-password", json={"email": unverified_user["email"]})
    token = _token_from(sent_emails[-1], "/reset-password")

    response = client.post("/api/auth/reset-password", json={"token": token, "password": "new-password-1"})
    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["user"]["email_verified"] is True  # le lien reçu prouve l'adresse

    login = {"email": unverified_user["email"]}
    assert client.post("/api/auth/login", json={**login, "password": "new-password-1"}).status_code == 200
    assert client.post("/api/auth/login", json={**login, "password": "password123"}).status_code == 401

    replay = client.post("/api/auth/reset-password", json={"token": token, "password": "another-pass-2"})
    assert replay.status_code == 400


def test_reset_password_validates_input(client, registered_user, sent_emails):
    client.post("/api/auth/forgot-password", json={"email": registered_user["email"]})
    token = _token_from(sent_emails[-1], "/reset-password")

    assert client.post("/api/auth/reset-password", json={"token": token, "password": "short"}).status_code == 422
    assert client.post("/api/auth/reset-password", json={"token": "nope", "password": "long-enough"}).status_code == 400


# --- Liaison Google -----------------------------------------------------------


def test_google_login_on_unverified_account_drops_foreign_password(client, unverified_user, db_session):
    profile = {"sub": "g-1", "email": unverified_user["email"], "name": "Victime"}
    user = upsert_google_user(db_session, profile)

    assert user.email_verified is True
    assert user.password_hash is None
    login = {"email": unverified_user["email"], "password": unverified_user["password"]}
    assert client.post("/api/auth/login", json=login).status_code == 401


def test_google_login_keeps_password_of_verified_account(client, registered_user, db_session):
    upsert_google_user(db_session, {"sub": "g-2", "email": registered_user["email"]})
    login = {"email": registered_user["email"], "password": registered_user["password"]}
    assert client.post("/api/auth/login", json=login).status_code == 200


# --- Migration ----------------------------------------------------------------


def test_migration_marks_existing_users_verified(db_session):
    db_session.add(User(id=uuid.uuid4(), email="legacy@example.com"))
    db_session.commit()
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE users DROP COLUMN email_verified_at"))

    for _ in range(2):  # idempotente
        with engine.begin() as conn:
            upgrade_legacy_schema(conn)

    db_session.expire_all()
    legacy = db_session.query(User).filter_by(email="legacy@example.com").one()
    assert legacy.email_verified is True


def test_account_deletion_removes_history(client, auth_headers, db_session, registered_user):
    user_id = uuid.UUID(registered_user["user"]["id"])
    db_session.add(
        ComparisonRecord.from_analysis(user_id=user_id, offer_text="Offre", cv_text="CV", items=[], summary={})
    )
    db_session.add(
        InterviewRecord.from_session(
            user_id=user_id, job_text="Offre", cv_text="CV", questions=[], answers=[], analysis={}
        )
    )
    db_session.commit()

    assert client.delete("/api/auth/me", headers=auth_headers).status_code == 200
    db_session.expire_all()
    assert db_session.query(ComparisonRecord).count() == 0
    assert db_session.query(InterviewRecord).count() == 0
