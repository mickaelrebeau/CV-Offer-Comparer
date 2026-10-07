import json
import uuid
from unittest.mock import patch
from uuid import UUID

import pytest
from sqlalchemy import select

from app.models.application_record import ApplicationRecord
from app.models.comparison_record import ComparisonRecord
from app.models.cover_letter_record import CoverLetterRecord
from app.models.interview_record import InterviewRecord
from app.models.user import User

OFFER = "Développeur Python senior\nAcme — Lyon\nFastAPI, PostgreSQL, Docker."
COMPARE = "app.services.comparison_service.ai_service.compare_offer_and_cv"
LETTER = "app.services.cover_letter_service.ai_service.generate_cover_letter"


def _other_headers(client):
    email = f"other-{uuid.uuid4().hex[:8]}@example.com"
    token = client.post("/api/auth/register", json={"email": email, "password": "password123"}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _create(client, headers, **body):
    return client.post("/api/applications", headers=headers, json=body)


def _comparison(db_session, user_id, score=0.5, **extra):
    record = ComparisonRecord.from_analysis(
        user_id=UUID(str(user_id)),
        offer_text=OFFER,
        cv_text="CV",
        offer_url="https://jobs.example.com/42",
        items=[],
        summary={"matchPercentage": score},
        **extra,
    )
    db_session.add(record)
    db_session.commit()
    db_session.refresh(record)
    return record


# --- CRUD ---------------------------------------------------------------------


def test_routes_require_auth(client):
    assert client.get("/api/applications").status_code in (401, 403)
    assert client.post("/api/applications", json={"title": "x"}).status_code in (401, 403)


def test_create_list_update_delete(client, auth_headers):
    created = _create(
        client, auth_headers, title="Dev Python", company="Acme", offer_url="https://jobs.example.com/1", offer_text=OFFER
    )
    assert created.status_code == 200, created.text
    application = created.json()
    assert application["status"] == "to_apply"
    assert application["applied_at"] is None
    assert application["comparisons"] == application["interviews"] == application["cover_letters"] == []

    listing = client.get("/api/applications", headers=auth_headers).json()
    assert listing["total"] == 1
    assert listing["items"][0]["title"] == "Dev Python"
    assert "offer_text" not in listing["items"][0]

    updated = client.patch(
        f"/api/applications/{application['id']}",
        headers=auth_headers,
        json={"status": "applied", "notes": "  Relancer lundi  "},
    ).json()
    assert updated["status"] == "applied"
    assert updated["notes"] == "Relancer lundi"
    assert updated["applied_at"] is not None
    assert updated["company"] == "Acme"  # champs non envoyés inchangés

    # La date de candidature n'est pas écrasée aux étapes suivantes
    later = client.patch(f"/api/applications/{application['id']}", headers=auth_headers, json={"status": "interview"}).json()
    assert later["applied_at"] == updated["applied_at"]

    assert client.delete(f"/api/applications/{application['id']}", headers=auth_headers).json() == {"success": True}
    assert client.get(f"/api/applications/{application['id']}", headers=auth_headers).status_code == 404


def test_title_defaults_to_first_offer_line(client, auth_headers):
    application = _create(client, auth_headers, offer_text="\n  Développeur Python senior  \nAcme").json()
    assert application["title"] == "Développeur Python senior"


@pytest.mark.parametrize(
    "body,code",
    [
        ({}, "application.title_missing"),
        ({"title": "Dev", "status": "ghosted"}, "application.invalid_status"),
    ],
)
def test_create_validation(client, auth_headers, body, code):
    response = _create(client, auth_headers, **body)
    assert response.status_code == 400
    assert response.json()["code"] == code


@pytest.mark.parametrize(
    "body,code",
    [({"title": "  "}, "application.title_missing"), ({"status": "unknown"}, "application.invalid_status")],
)
def test_update_validation(client, auth_headers, body, code):
    application = _create(client, auth_headers, title="Dev").json()
    response = client.patch(f"/api/applications/{application['id']}", headers=auth_headers, json=body)
    assert response.status_code == 400
    assert response.json()["code"] == code


def test_unsafe_offer_url_is_dropped(client, auth_headers):
    application = _create(client, auth_headers, title="Dev", offer_url="javascript:alert(1)").json()
    assert application["offer_url"] is None


def test_applications_are_scoped_to_owner(client, auth_headers):
    application = _create(client, auth_headers, title="Dev").json()
    other = _other_headers(client)
    path = f"/api/applications/{application['id']}"

    assert client.get("/api/applications", headers=other).json()["total"] == 0
    for method, kwargs in (("get", {}), ("patch", {"json": {"status": "offer"}}), ("delete", {})):
        response = getattr(client, method)(path, headers=other, **kwargs)
        assert response.status_code == 404
        assert response.json()["code"] == "application.not_found"


# --- Création après une analyse et rattachements -----------------------------


def test_follow_after_analysis_links_comparison_and_reuses_offer(client, auth_headers, db_session, registered_user):
    comparison = _comparison(db_session, registered_user["user"]["id"], score=0.62)

    application = _create(client, auth_headers, comparison_id=str(comparison.id), company="Acme").json()

    assert application["title"] == "Développeur Python senior"
    assert application["offer_url"] == "https://jobs.example.com/42"
    assert application["offer_text"] == OFFER
    assert [item["id"] for item in application["comparisons"]] == [str(comparison.id)]
    assert application["last_score"] == pytest.approx(0.62)
    assert application["comparison_count"] == 1


def test_follow_rejects_comparison_of_another_user(client, auth_headers, db_session):
    other = _other_headers(client)
    other_id = client.get("/api/auth/me", headers=other).json()["id"]
    theirs = _comparison(db_session, other_id)

    response = _create(client, auth_headers, comparison_id=str(theirs.id))

    assert response.status_code == 404
    assert response.json()["code"] == "history.comparison_not_found"
    assert db_session.scalars(select(ApplicationRecord)).all() == []


def test_new_analysis_and_letter_are_linked(client, auth_headers, db_session):
    application = _create(client, auth_headers, title="Dev", offer_text=OFFER).json()
    result = {"items": [], "summary": {"matchPercentage": 0.8, "totalItems": 0}}

    with patch(COMPARE, return_value=result):
        with client.stream(
            "POST",
            "/api/compare-stream",
            headers=auth_headers,
            json={"offer_text": OFFER, "cv_text": "CV", "application_id": application["id"]},
        ) as response:
            body = "".join(response.iter_text())
    comparison_id = [json.loads(line[6:]) for line in body.splitlines() if line.startswith("data: ")][-1]["comparison_id"]

    letter = {"subject": "Objet", "opening": "Bonjour", "body": ["Corps"], "closing": "Fin", "language": "fr"}
    with patch(LETTER, return_value=letter):
        with client.stream(
            "POST",
            "/api/cover-letter",
            headers=auth_headers,
            data={"job_text": OFFER, "cv_text": "CV", "application_id": application["id"]},
        ) as response:
            "".join(response.iter_text())

    detail = client.get(f"/api/applications/{application['id']}", headers=auth_headers).json()
    assert [item["id"] for item in detail["comparisons"]] == [comparison_id]
    assert detail["last_score"] == pytest.approx(0.8)
    assert detail["cover_letter_count"] == 1
    assert detail["cover_letters"][0]["subject"] == "Objet"


def test_interview_is_linked(client, auth_headers, db_session, monkeypatch):
    application = _create(client, auth_headers, title="Dev").json()

    async def fake_analyze(self, questions, answers, cv_text, job_text):
        return {"success": True, "analysis": {"score_global": 7}}

    monkeypatch.setattr("app.services.interview_service.InterviewService.analyze_responses", fake_analyze)
    response = client.post(
        "/api/interview/analyze-responses",
        headers=auth_headers,
        data={
            "questions": json.dumps([{"id": 1, "question": "Q"}]),
            "answers": json.dumps([{"question": "Q", "answer": "R"}]),
            "cv_text": "CV",
            "job_text": OFFER,
            "application_id": application["id"],
        },
    )

    assert response.status_code == 200, response.text
    record = db_session.get(InterviewRecord, UUID(response.json()["interview_id"]))
    assert str(record.application_id) == application["id"]


def test_linking_to_another_users_application_is_refused(client, auth_headers):
    theirs = _create(client, _other_headers(client), title="Dev").json()
    with patch(COMPARE) as compare:
        response = client.post(
            "/api/compare-stream",
            headers=auth_headers,
            json={"offer_text": OFFER, "cv_text": "CV", "application_id": theirs["id"]},
        )
    assert response.status_code == 404
    assert response.json()["code"] == "application.not_found"
    compare.assert_not_called()


def test_rescore_inherits_application(client, auth_headers, db_session):
    application = _create(client, auth_headers, title="Dev", offer_text=OFFER).json()
    user_id = client.get("/api/auth/me", headers=auth_headers).json()["id"]
    parent = _comparison(db_session, user_id, application_id=UUID(application["id"]))

    with patch(COMPARE, return_value={"items": [], "summary": {"matchPercentage": 0.9}}):
        with client.stream(
            "POST",
            "/api/compare-stream",
            headers=auth_headers,
            json={"offer_text": OFFER, "cv_text": "CV v2", "parent_comparison_id": str(parent.id)},
        ) as response:
            "".join(response.iter_text())

    detail = client.get(f"/api/applications/{application['id']}", headers=auth_headers).json()
    assert detail["comparison_count"] == 2
    assert detail["last_score"] == pytest.approx(0.9)


def test_deleting_application_keeps_linked_history(client, auth_headers, db_session, registered_user):
    comparison = _comparison(db_session, registered_user["user"]["id"])
    application = _create(client, auth_headers, comparison_id=str(comparison.id)).json()

    client.delete(f"/api/applications/{application['id']}", headers=auth_headers)

    db_session.expire_all()
    kept = db_session.get(ComparisonRecord, comparison.id)
    assert kept is not None
    assert kept.application_id is None


def test_account_deletion_removes_applications(client, auth_headers, db_session, registered_user):
    _create(client, auth_headers, title="Dev")
    user_id = UUID(registered_user["user"]["id"])

    db_session.delete(db_session.get(User, user_id))
    db_session.commit()

    assert db_session.scalars(select(ApplicationRecord).where(ApplicationRecord.user_id == user_id)).all() == []
    assert db_session.scalars(select(CoverLetterRecord).where(CoverLetterRecord.user_id == user_id)).all() == []
