import json
import uuid
from unittest.mock import patch
from uuid import UUID

import pytest
from sqlalchemy import select

from app.config import settings
from app.models.comparison_record import ComparisonRecord
from app.models.cv_optimization_record import CvOptimizationRecord
from app.services.cv_optimizer_service import NoSuggestionError, locate_in_cv, validate_optimization

OPTIMIZE = "app.services.cv_optimizer_service.ai_service.optimize_cv"
JOB = "Développeur Python senior — FastAPI, PostgreSQL, Docker, CI/CD. Équipe produit à Lyon."
CV = (
    "Jeanne Martin\n"
    "Expérience\n"
    "- Développement d'API   Python pour une plateforme e-commerce (2019-2024)\n"
    "- Mise en place de tests automatisés\n"
    "Compétences : Python, SQL, Git"
)

RAW = {
    "summary": "Mettre en avant FastAPI et l'automatisation déjà présentes dans le CV.",
    "suggestions": [
        {
            "section": "Expérience",
            "original": "Développement d'API Python pour une plateforme e-commerce (2019-2024)",
            "proposed": "Conception d'API REST en Python pour une plateforme e-commerce à fort trafic (2019-2024)",
            "requirement": "API Python",
            "rationale": "Reprend le vocabulaire de l'offre.",
        },
        {
            "section": "Expérience",
            "original": "Mise en place de tests automatisés",
            "proposed": "Mise en place de tests automatisés intégrés à la chaîne CI",
            "requirement": "CI/CD",
            "rationale": "Relie les tests à la CI demandée.",
        },
    ],
}


def _events(body: str) -> list[dict]:
    return [json.loads(line[6:]) for line in body.splitlines() if line.startswith("data: ")]


def _optimize(client, headers, **body):
    payload = {"cv_text": CV, "job_text": JOB, **body}
    with client.stream("POST", "/api/cv-optimizer", headers=headers, json=payload) as response:
        return response, _events("".join(response.iter_text())) if response.status_code == 200 else []


def _records(db_session, registered_user):
    db_session.expire_all()
    user_id = UUID(registered_user["user"]["id"])
    return db_session.scalars(select(CvOptimizationRecord).where(CvOptimizationRecord.user_id == user_id)).all()


# --- Validation de la sortie du LLM ---------------------------------------------


def test_locate_in_cv_tolerates_whitespace_and_returns_exact_excerpt():
    assert locate_in_cv("Développement d'API Python pour", CV) == "Développement d'API   Python pour"
    assert locate_in_cv("Développement de microservices Go", CV) is None
    assert locate_in_cv("   ", CV) is None


def test_validate_keeps_real_excerpts_with_ids():
    result = validate_optimization(RAW, CV)
    assert result["summary"].startswith("Mettre en avant")
    assert [s["id"] for s in result["suggestions"]] == ["s1", "s2"]
    # Extrait tel qu'il figure dans le CV, pour pouvoir l'y remplacer
    assert result["suggestions"][0]["original"] == "Développement d'API   Python pour une plateforme e-commerce (2019-2024)"


@pytest.mark.parametrize(
    "suggestion",
    [
        # Extrait absent du CV (paraphrase ou invention)
        {"original": "Lead technique d'une équipe de 8 personnes", "proposed": "Lead technique"},
        # Chiffre absent du CV
        {"original": "Mise en place de tests automatisés", "proposed": "Tests automatisés couvrant 95 % du code"},
        # Proposition vide ou identique
        {"original": "Mise en place de tests automatisés", "proposed": "  "},
        {"original": "Mise en place de tests automatisés", "proposed": "Mise en place de  tests automatisés"},
        # Format invalide
        "texte libre",
    ],
)
def test_validate_rejects_unsafe_or_unusable_suggestions(suggestion):
    with pytest.raises(NoSuggestionError):
        validate_optimization({"summary": "", "suggestions": [suggestion]}, CV)


def test_validate_deduplicates_and_caps():
    duplicate = {**RAW["suggestions"][1], "proposed": "Autre formulation des tests automatisés"}
    result = validate_optimization({"suggestions": [*RAW["suggestions"], duplicate]}, CV)
    assert len(result["suggestions"]) == 2

    many = [{"original": "Python", "proposed": f"Python avancé, variante {letter}"} for letter in "ABC"]
    assert len(validate_optimization({"suggestions": many}, CV)["suggestions"]) == 1


@pytest.mark.parametrize("raw", [None, [], {"suggestions": "x"}, {}])
def test_validate_rejects_unstructured_output(raw):
    with pytest.raises(NoSuggestionError):
        validate_optimization(raw, CV)


# --- Endpoint -------------------------------------------------------------------


def test_requires_auth(client):
    assert client.post("/api/cv-optimizer", json={"cv_text": CV, "job_text": JOB}).status_code in (401, 403)
    assert client.get("/api/cv-optimizations").status_code in (401, 403)


def test_requires_verified_email(client, unverified_user):
    headers = {"Authorization": f"Bearer {unverified_user['token']}"}
    response = client.post("/api/cv-optimizer", json={"cv_text": CV, "job_text": JOB}, headers=headers)
    assert response.status_code == 403


def test_streams_suggestions_and_persists(client, auth_headers, db_session, registered_user):
    with patch(OPTIMIZE, return_value=RAW) as optimize:
        response, events = _optimize(client, auth_headers, offer_url="https://jobs.example.com/42")

    assert response.status_code == 200
    assert optimize.call_args.args[:2] == (CV, JOB)
    suggestions = [event["suggestion"] for event in events if event["type"] == "suggestion"]
    assert [s["id"] for s in suggestions] == ["s1", "s2"]
    result = next(event for event in events if event["type"] == "result")
    assert events[-1]["type"] == "complete"

    [record] = _records(db_session, registered_user)
    assert str(record.id) == result["id"]
    assert record.suggestion_count == 2
    assert record.suggestions == suggestions
    assert record.offer_url == "https://jobs.example.com/42"
    assert record.comparison_id is None


def test_from_comparison_targets_its_gaps_and_texts(client, auth_headers, db_session, registered_user):
    comparison = ComparisonRecord.from_analysis(
        user_id=UUID(registered_user["user"]["id"]),
        offer_text=JOB,
        cv_text=CV,
        offer_url="https://jobs.example.com/7",
        items=[
            {"category": "skills", "offerText": "Python", "status": "match"},
            {"category": "skills", "offerText": "Docker", "status": "unclear"},
            {"category": "skills", "offerText": "CI/CD", "status": "missing"},
        ],
        summary={"matchPercentage": 0.33},
    )
    db_session.add(comparison)
    db_session.commit()

    with patch(OPTIMIZE, return_value=RAW) as optimize:
        response, _ = _optimize(client, auth_headers, cv_text="", job_text="", comparison_id=str(comparison.id))

    assert response.status_code == 200
    cv, job, gaps = optimize.call_args.args
    assert (cv, job) == (CV, JOB)
    # Manquantes d'abord, puis floues ; les correspondances ne sont pas ciblées
    assert [gap["offerText"] for gap in gaps] == ["CI/CD", "Docker"]
    [record] = _records(db_session, registered_user)
    assert record.comparison_id == comparison.id
    assert record.offer_url == "https://jobs.example.com/7"


def test_rejects_comparison_of_another_user(client, auth_headers, db_session):
    email = f"other-{uuid.uuid4().hex[:8]}@example.com"
    other = client.post("/api/auth/register", json={"email": email, "password": "password123"}).json()
    comparison = ComparisonRecord.from_analysis(
        user_id=UUID(other["user"]["id"]), offer_text=JOB, cv_text=CV, items=[], summary={}
    )
    db_session.add(comparison)
    db_session.commit()

    with patch(OPTIMIZE) as optimize:
        response = client.post("/api/cv-optimizer", headers=auth_headers, json={"comparison_id": str(comparison.id)})

    assert response.status_code == 404
    assert response.json()["code"] == "history.comparison_not_found"
    optimize.assert_not_called()


@pytest.mark.parametrize(
    "body,status,code",
    [
        ({"job_text": "  "}, 400, "interview.job_empty"),
        ({"cv_text": ""}, 400, "cover_letter.cv_missing"),
        ({"cv_text": "x" * 50_001}, 413, "cover_letter.text_too_long"),
    ],
)
def test_validation(client, auth_headers, db_session, registered_user, body, status, code):
    with patch(OPTIMIZE) as optimize:
        response = client.post("/api/cv-optimizer", headers=auth_headers, json={"cv_text": CV, "job_text": JOB, **body})
    assert response.status_code == status
    assert response.json()["code"] == code
    optimize.assert_not_called()
    assert _records(db_session, registered_user) == []


def test_no_valid_suggestion_sends_error_without_history(client, auth_headers, db_session, registered_user):
    invented = {"suggestions": [{"original": "Directeur technique chez Google", "proposed": "CTO"}]}
    with patch(OPTIMIZE, return_value=invented):
        response, events = _optimize(client, {**auth_headers, "Accept-Language": "en"})

    assert response.status_code == 200
    assert events[-1]["type"] == "error"
    assert events[-1]["code"] == "cv_optimizer.no_suggestions"
    assert events[-1]["message"].startswith("No reliable rewrite")
    assert _records(db_session, registered_user) == []


def test_llm_failure_hides_details(client, auth_headers, db_session, registered_user):
    with patch(OPTIMIZE, side_effect=RuntimeError("clé Gemini invalide")):
        _, events = _optimize(client, auth_headers)
    assert events[-1]["code"] == "cv_optimizer.failed"
    assert "Gemini" not in events[-1]["message"]
    assert _records(db_session, registered_user) == []


def test_daily_quota(client, auth_headers, monkeypatch):
    monkeypatch.setattr(settings, "DAILY_QUOTA_CV_OPTIMIZER", 1)
    with patch(OPTIMIZE, return_value=RAW):
        first, _ = _optimize(client, auth_headers)
        second = client.post("/api/cv-optimizer", headers=auth_headers, json={"cv_text": CV, "job_text": JOB})
    assert first.status_code == 200
    assert second.status_code == 429


# --- Historique -----------------------------------------------------------------


def test_history_list_get_delete_are_scoped_to_owner(client, auth_headers, db_session, registered_user):
    with patch(OPTIMIZE, return_value=RAW):
        _, events = _optimize(client, auth_headers)
    optimization_id = next(event for event in events if event["type"] == "result")["id"]

    listing = client.get("/api/cv-optimizations", headers=auth_headers).json()
    assert listing["total"] == 1
    assert listing["items"][0]["suggestion_count"] == 2
    assert "suggestions" not in listing["items"][0]

    detail = client.get(f"/api/cv-optimizations/{optimization_id}", headers=auth_headers).json()
    assert detail["cv_text"] == CV
    assert len(detail["suggestions"]) == 2

    email = f"other-{uuid.uuid4().hex[:8]}@example.com"
    token = client.post("/api/auth/register", json={"email": email, "password": "password123"}).json()["access_token"]
    other = {"Authorization": f"Bearer {token}"}
    assert client.get(f"/api/cv-optimizations/{optimization_id}", headers=other).status_code == 404
    assert client.delete(f"/api/cv-optimizations/{optimization_id}", headers=other).status_code == 404

    assert client.delete(f"/api/cv-optimizations/{optimization_id}", headers=auth_headers).json() == {"success": True}
    assert client.get(f"/api/cv-optimizations/{optimization_id}", headers=auth_headers).status_code == 404
