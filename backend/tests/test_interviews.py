from uuid import UUID

from app.models.interview_record import InterviewRecord


def test_list_interviews_empty(client, auth_headers):
    response = client.get("/api/interviews", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


def test_list_and_get_interview(client, auth_headers, db_session, registered_user):
    user_id = UUID(registered_user["user"]["id"])
    record = InterviewRecord.from_session(
        user_id=user_id,
        job_text="Développeur Python senior — FastAPI, Postgres",
        cv_text="Développeur fullstack Python avec 5 ans d'expérience FastAPI",
        questions=[
            {"text": "Parlez-moi de FastAPI", "category": "Compétences"},
            {"text": "Décrivez un projet récent", "category": "Expérience"},
        ],
        answers=[
            {
                "questionIndex": 0,
                "question": "Parlez-moi de FastAPI",
                "category": "Compétences",
                "answer": "J'ai bâti plusieurs APIs FastAPI en production.",
                "time": 45,
            }
        ],
        analysis={
            "score_global": 8,
            "points_forts": ["Clarté technique"],
            "points_amelioration": ["Exemples chiffrés"],
            "suggestions": [],
            "conseils_specifiques": [],
        },
        duration_seconds=320,
    )
    db_session.add(record)
    db_session.commit()
    db_session.refresh(record)

    listing = client.get("/api/interviews", headers=auth_headers)
    assert listing.status_code == 200
    payload = listing.json()
    assert payload["total"] == 1
    assert payload["items"][0]["id"] == str(record.id)
    assert payload["items"][0]["score_global"] == 8
    assert payload["items"][0]["num_questions"] == 2
    assert payload["items"][0]["duration_seconds"] == 320

    detail = client.get(f"/api/interviews/{record.id}", headers=auth_headers)
    assert detail.status_code == 200
    body = detail.json()
    assert body["job_text"].startswith("Développeur Python")
    assert len(body["questions"]) == 2
    assert body["analysis"]["score_global"] == 8

    deleted = client.delete(f"/api/interviews/{record.id}", headers=auth_headers)
    assert deleted.status_code == 200
    assert deleted.json()["success"] is True

    missing = client.get(f"/api/interviews/{record.id}", headers=auth_headers)
    assert missing.status_code == 404


def test_interviews_require_auth(client):
    response = client.get("/api/interviews")
    assert response.status_code in (401, 403)
