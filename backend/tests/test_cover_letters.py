import json
from unittest.mock import patch
from uuid import UUID

import pytest
from sqlalchemy import select

from app.config import settings
from app.models.cover_letter_record import CoverLetterRecord
from tests.pdf_factory import make_pdf

GENERATE = "app.services.cover_letter_service.ai_service.generate_cover_letter"
JOB = "Développeur Python senior — FastAPI, PostgreSQL, Docker. Équipe produit à Lyon."
CV = "Jeanne Martin — développeuse Python, 6 ans d'expérience FastAPI et PostgreSQL."

FAKE_LETTER = {
    "subject": "Objet : candidature au poste de développeur Python senior",
    "greeting": "Madame, Monsieur,",
    "opening": "Développeuse Python depuis six ans, je souhaite rejoindre votre équipe produit.",
    "body": [
        "J'ai conçu des API FastAPI adossées à PostgreSQL servant 2 millions de requêtes par jour.",
        "J'ai conteneurisé ces services avec Docker et outillé leur déploiement continu.",
    ],
    "closing": "Je serais ravie d'échanger avec vous lors d'un entretien.",
    "signoff": "Je vous prie d'agréer, Madame, Monsieur, mes salutations distinguées.",
    "signature": "Jeanne Martin",
    "language": "fr",
}


def _events(body: str) -> list[dict]:
    return [json.loads(line[6:]) for line in body.splitlines() if line.startswith("data: ")]


def _generate(client, headers, data=None, files=None):
    payload = {"job_text": JOB, "cv_text": CV, **(data or {})}
    with client.stream(
        "POST",
        "/api/cover-letter",
        headers={**headers, "Accept": "text/event-stream"},
        data=payload,
        files=files,
    ) as response:
        body = "".join(response.iter_text())
    return response, body


def _records(db_session, user):
    db_session.expire_all()
    return db_session.scalars(
        select(CoverLetterRecord).where(CoverLetterRecord.user_id == UUID(user["user"]["id"]))
    ).all()


def _save(db_session, user, **overrides):
    record = CoverLetterRecord.from_generation(
        user_id=UUID(user["user"]["id"]),
        job_text=JOB,
        cv_text=CV,
        tone="professional",
        length="standard",
        letter={**FAKE_LETTER, **overrides},
    )
    db_session.add(record)
    db_session.commit()
    db_session.refresh(record)
    return record


# --- Génération ---------------------------------------------------------------


def test_generate_streams_sections_and_persists_history(client, auth_headers, db_session, registered_user):
    with patch(GENERATE, return_value=FAKE_LETTER) as generate:
        response, body = _generate(client, auth_headers, {"tone": "warm", "length": "short", "language": "fr"})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    generate.assert_called_once_with(CV, JOB, tone="warm", length="short", language="fr")

    events = _events(body)
    sections = [e["section"] for e in events if e["type"] == "section"]
    assert [s["key"] for s in sections] == [
        "subject", "greeting", "opening", "body", "body", "closing", "signoff", "signature",
    ]
    assert events[-1] == {"type": "complete"}

    final = next(e for e in events if e["type"] == "letter")
    assert final["letter"] == FAKE_LETTER

    rows = _records(db_session, registered_user)
    assert len(rows) == 1
    assert final["id"] == str(rows[0].id)
    assert rows[0].tone == "warm"
    assert rows[0].length == "short"
    assert rows[0].language == "fr"
    assert rows[0].subject.startswith("Objet : candidature")
    assert rows[0].word_count > 50
    assert rows[0].cv_text == CV
    assert rows[0].job_text == JOB


def test_generate_from_txt_file(client, auth_headers, db_session, registered_user):
    files = {"cv_file": ("cv.txt", CV.encode(), "text/plain")}
    with patch(GENERATE, return_value=FAKE_LETTER) as generate:
        response, _ = _generate(client, auth_headers, {"cv_text": ""}, files=files)

    assert response.status_code == 200
    assert generate.call_args.args[0] == CV
    assert _records(db_session, registered_user)[0].cv_text == CV


def test_generate_from_pdf_file(client, auth_headers, db_session, registered_user):
    files = {"cv_file": ("cv.pdf", make_pdf("Jeanne Martin Python FastAPI"), "application/pdf")}
    with patch(GENERATE, return_value=FAKE_LETTER) as generate:
        response, _ = _generate(client, auth_headers, {"cv_text": ""}, files=files)

    assert response.status_code == 200
    assert "Jeanne Martin" in generate.call_args.args[0]


def test_gemini_failure_sends_error_event_without_history(client, auth_headers, db_session, registered_user):
    with patch(GENERATE, side_effect=RuntimeError("Lettre Gemini incomplète")):
        response, body = _generate(client, {**auth_headers, "Accept-Language": "en"})

    assert response.status_code == 200
    events = _events(body)
    assert events[-1]["type"] == "error"
    assert "Gemini incomplète" not in events[-1]["message"]  # pas de détail technique côté client
    assert events[-1]["message"].startswith("The cover letter could not be generated")
    assert _records(db_session, registered_user) == []


# --- Validation ---------------------------------------------------------------


@pytest.mark.parametrize(
    "data,files,status,code",
    [
        ({"job_text": "   "}, None, 400, "interview.job_empty"),
        ({"cv_text": ""}, None, 400, "cover_letter.cv_missing"),
        ({"tone": "sarcastic"}, None, 400, "cover_letter.invalid_option"),
        ({"length": "epic"}, None, 400, "cover_letter.invalid_option"),
        ({"language": "de"}, None, 400, "cover_letter.invalid_option"),
        ({"job_text": "x" * 50_001}, None, 413, "cover_letter.text_too_long"),
        ({"cv_text": "x" * 50_001}, None, 413, "cover_letter.text_too_long"),
        ({}, {"cv_file": ("cv.docx", b"PK", "application/octet-stream")}, 400, "upload.cv_format"),
        ({}, {"cv_file": ("cv.pdf", b"%PDF-1.4 broken", "application/pdf")}, 400, "upload.pdf_unreadable"),
        ({}, {"cv_file": ("cv.txt", b"   ", "text/plain")}, 400, "upload.empty_file"),
    ],
)
def test_generate_validation(client, auth_headers, db_session, registered_user, data, files, status, code):
    with patch(GENERATE) as generate:
        response = client.post(
            "/api/cover-letter",
            headers=auth_headers,
            data={"job_text": JOB, "cv_text": CV, **data},
            files=files,
        )

    assert response.status_code == status, response.text
    assert response.json()["code"] == code
    generate.assert_not_called()
    assert _records(db_session, registered_user) == []


def test_generate_rejects_oversized_file(client, auth_headers, monkeypatch):
    monkeypatch.setattr(settings, "MAX_FILE_SIZE", 1024)
    files = {"cv_file": ("cv.txt", b"x" * 2048, "text/plain")}
    with patch(GENERATE) as generate:
        response = client.post("/api/cover-letter", headers=auth_headers, data={"job_text": JOB}, files=files)

    assert response.status_code == 413
    assert response.json()["code"] == "upload.too_large"
    generate.assert_not_called()


# --- Authentification et limites ---------------------------------------------


def test_generate_requires_auth(client):
    response = client.post("/api/cover-letter", data={"job_text": JOB, "cv_text": CV})
    assert response.status_code in (401, 403)


def test_generate_requires_verified_email(client, unverified_user):
    headers = {"Authorization": f"Bearer {unverified_user['token']}"}
    with patch(GENERATE) as generate:
        response = client.post("/api/cover-letter", headers=headers, data={"job_text": JOB, "cv_text": CV})

    assert response.status_code == 403
    assert response.json()["code"] == "auth.email_not_verified"
    generate.assert_not_called()


def test_generate_daily_quota(client, auth_headers, monkeypatch):
    monkeypatch.setattr(settings, "RATE_LIMIT_ENABLED", True)
    monkeypatch.setattr(settings, "RATE_LIMIT_USER_PER_MINUTE", 100)
    monkeypatch.setattr(settings, "DAILY_QUOTA_COVER_LETTER", 1)
    with patch(GENERATE, return_value=FAKE_LETTER):
        assert _generate(client, auth_headers)[0].status_code == 200
        blocked = client.post("/api/cover-letter", headers=auth_headers, data={"job_text": JOB, "cv_text": CV})

    assert blocked.status_code == 429
    assert blocked.json()["code"] == "rate.daily_quota"
    assert int(blocked.headers["retry-after"]) >= 1


@pytest.mark.parametrize(
    "method,path",
    [
        ("get", "/api/cover-letters"),
        ("get", "/api/cover-letters/00000000-0000-0000-0000-000000000000"),
        ("delete", "/api/cover-letters/00000000-0000-0000-0000-000000000000"),
    ],
)
def test_history_requires_auth(client, method, path):
    assert getattr(client, method)(path).status_code in (401, 403)


# --- Historique ---------------------------------------------------------------


def test_list_cover_letters_empty(client, auth_headers):
    response = client.get("/api/cover-letters", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == {"items": [], "total": 0, "limit": 20, "offset": 0}


def test_list_get_delete_cover_letter(client, auth_headers, db_session, registered_user):
    record = _save(db_session, registered_user)

    listing = client.get("/api/cover-letters", headers=auth_headers).json()
    assert listing["total"] == 1
    item = listing["items"][0]
    assert item["id"] == str(record.id)
    assert item["subject"] == FAKE_LETTER["subject"]
    assert item["tone"] == "professional"
    assert item["word_count"] == record.word_count
    assert "letter" not in item and "cv_text" not in item

    detail = client.get(f"/api/cover-letters/{record.id}", headers=auth_headers)
    assert detail.status_code == 200
    assert detail.json()["letter"] == FAKE_LETTER
    assert detail.json()["job_text"] == JOB

    deleted = client.delete(f"/api/cover-letters/{record.id}", headers=auth_headers)
    assert deleted.status_code == 200
    assert deleted.json() == {"success": True}

    missing = client.get(f"/api/cover-letters/{record.id}", headers={**auth_headers, "Accept-Language": "en"})
    assert missing.status_code == 404
    assert missing.json() == {"detail": "Cover letter not found", "code": "history.cover_letter_not_found"}


def test_list_is_paginated_newest_first(client, auth_headers, db_session, registered_user):
    for index in range(3):
        _save(db_session, registered_user, subject=f"Lettre {index}")

    page = client.get("/api/cover-letters?limit=2&offset=0", headers=auth_headers).json()
    assert page["total"] == 3
    assert len(page["items"]) == 2
    rest = client.get("/api/cover-letters?limit=2&offset=2", headers=auth_headers).json()
    assert len(rest["items"]) == 1


def test_cover_letters_are_private(client, db_session, registered_user):
    record = _save(db_session, registered_user)
    other = client.post("/api/auth/register", json={"email": "other@example.com", "password": "password123"})
    headers = {"Authorization": f"Bearer {other.json()['access_token']}"}

    assert client.get("/api/cover-letters", headers=headers).json()["total"] == 0
    assert client.get(f"/api/cover-letters/{record.id}", headers=headers).status_code == 404
    assert client.delete(f"/api/cover-letters/{record.id}", headers=headers).status_code == 404
    assert len(_records(db_session, registered_user)) == 1


def test_account_deletion_removes_cover_letters(client, auth_headers, db_session, registered_user):
    _save(db_session, registered_user)

    assert client.delete("/api/auth/me", headers=auth_headers).status_code == 200
    assert _records(db_session, registered_user) == []
