import json
import re

import pytest

from app.config import settings
from app.i18n import MESSAGES, negotiate_locale
from app.services.ai_service import ai_service
from tests.pdf_factory import make_pdf

EN = {"Accept-Language": "en-US,en;q=0.9"}


@pytest.mark.parametrize(
    "header,expected",
    [
        (None, "fr"),
        ("", "fr"),
        ("en", "en"),
        ("en-GB,en;q=0.9", "en"),
        ("fr-FR,fr;q=0.9,en;q=0.8", "fr"),
        ("de-DE,de;q=0.9", "fr"),
        ("de;q=1,en;q=0.5,fr;q=0.4", "en"),
        ("fr;q=0.2,en;q=0.8", "en"),
        ("*", "fr"),
    ],
)
def test_negotiate_locale(header, expected):
    assert negotiate_locale(header) == expected


def test_catalog_has_same_placeholders_in_both_languages():
    for code, messages in MESSAGES.items():
        assert set(messages) == {"fr", "en"}, code
        fr, en = (sorted(re.findall(r"\{(\w+)\}", messages[lang])) for lang in ("fr", "en"))
        assert fr == en, code


def test_error_is_translated_with_stable_code(client):
    body = {"email": "ghost@example.com", "password": "wrong-password"}
    fr = client.post("/api/auth/login", json=body)
    en = client.post("/api/auth/login", json=body, headers=EN)

    assert fr.status_code == en.status_code == 401
    assert fr.json() == {"detail": "Email ou mot de passe incorrect", "code": "auth.invalid_credentials"}
    assert en.json() == {"detail": "Incorrect email or password", "code": "auth.invalid_credentials"}


def test_unverified_user_error_in_english(client, unverified_user):
    headers = {**EN, "Authorization": f"Bearer {unverified_user['token']}"}
    response = client.post("/api/compare-stream", headers=headers)
    assert response.status_code == 403
    assert response.json()["code"] == "auth.email_not_verified"
    assert response.json()["detail"] == "Confirm your email address to use this feature."


def test_rate_limit_error_keeps_retry_after(client, auth_headers, monkeypatch):
    monkeypatch.setattr(settings, "RATE_LIMIT_USER_PER_MINUTE", 1)
    files = {"file": ("cv.txt", b"x", "text/plain")}
    client.post("/api/upload-cv", files=files, headers={**auth_headers, **EN})
    blocked = client.post("/api/upload-cv", files=files, headers={**auth_headers, **EN})

    assert blocked.status_code == 429
    assert blocked.json()["code"] == "rate.too_many"
    assert blocked.json()["detail"].startswith("Too many requests")
    assert int(blocked.headers["retry-after"]) >= 1


def test_upload_messages_in_english(client, auth_headers):
    files = {"file": ("cv.pdf", make_pdf(None), "application/pdf")}
    body = client.post("/api/upload-cv", files=files, headers={**auth_headers, **EN}).json()
    assert body["success"] is False
    assert body["message"].startswith("This PDF contains no readable text")

    files = {"file": ("cv.pdf", make_pdf("Jane Doe"), "application/pdf")}
    body = client.post("/api/upload-cv", files=files, headers={**auth_headers, **EN}).json()
    assert re.fullmatch(r"Text extracted successfully \(\d+ characters\)", body["message"])


def test_too_large_upload_in_english(client, auth_headers, monkeypatch):
    monkeypatch.setattr(settings, "MAX_FILE_SIZE", 2 * 1024 * 1024)
    files = {"file": ("cv.pdf", b"x" * (3 * 1024 * 1024), "application/pdf")}
    response = client.post("/api/upload-cv", files=files, headers={**auth_headers, **EN})
    assert response.status_code == 413
    assert response.json() == {"detail": "The file is too large (2 MB max)", "code": "upload.too_large"}


def _sse_events(response):
    return [json.loads(line[6:]) for line in response.text.splitlines() if line.startswith("data: ")]


def test_comparison_stream_status_in_english(client, auth_headers, monkeypatch):
    monkeypatch.setattr(
        ai_service,
        "compare_offer_and_cv",
        lambda offer, cv: {"items": [{"id": 1}], "summary": {"matchPercentage": 1.0}},
    )
    response = client.post(
        "/api/compare-stream",
        json={"offer_text": "Python developer", "cv_text": "Python"},
        headers={**auth_headers, **EN},
    )
    statuses = [event["message"] for event in _sse_events(response) if event["type"] == "status"]
    assert statuses == [
        "Starting the analysis…",
        "ATS analysis by Gemini (extraction + matching)…",
        "Requirements analyzed: 1 — streaming results…",
    ]


def test_comparison_stream_hides_internal_errors(client, auth_headers, monkeypatch):
    def boom(offer, cv):
        raise RuntimeError("secret stack detail")

    monkeypatch.setattr(ai_service, "compare_offer_and_cv", boom)
    response = client.post(
        "/api/compare-stream",
        json={"offer_text": "Python developer", "cv_text": "Python"},
        headers={**auth_headers, **EN},
    )
    errors = [event for event in _sse_events(response) if event["type"] == "error"]
    assert errors == [{"type": "error", "message": "The analysis failed. Please try again in a moment."}]


def test_free_analysis_status_in_english(client):
    body = client.get("/api/free-analysis-status", headers=EN).json()
    assert body["message"] in ("You can run one free analysis", "You have already used your free analysis")


def test_emails_follow_request_language(client, registered_user, sent_emails):
    sent_emails.clear()
    client.post("/api/auth/forgot-password", json={"email": registered_user["email"]}, headers=EN)
    email = sent_emails[-1]
    assert email.subject == "Reset your password — Talento"
    assert "/en/reset-password?token=" in email.text
    assert "Or copy this link:" in email.html

    response = client.post("/api/auth/forgot-password", json={"email": "x@example.com"}, headers=EN)
    assert response.json()["message"].startswith("If an account exists")


def test_french_email_link_has_no_prefix(client, unverified_user, sent_emails):
    email = sent_emails[0]
    assert email.subject == "Confirmez votre adresse e-mail — Talento"
    assert re.search(r"https?://[^/\s]+/verify-email\?token=", email.text)
