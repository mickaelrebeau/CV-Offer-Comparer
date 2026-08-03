from uuid import UUID

from app.models.comparison_record import ComparisonRecord, _excerpt


def test_excerpt_truncates():
    long_text = "mot " * 100
    result = _excerpt(long_text, limit=40)
    assert len(result) <= 40
    assert result.endswith("…")


def test_list_comparisons_empty(client, auth_headers):
    response = client.get("/api/comparisons", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


def test_list_and_get_comparison(client, auth_headers, db_session, registered_user):
    user_id = UUID(registered_user["user"]["id"])
    record = ComparisonRecord.from_analysis(
        user_id=user_id,
        offer_text="Développeur Python senior — FastAPI, Postgres",
        cv_text="Développeur fullstack Python avec 5 ans d'expérience FastAPI",
        items=[
            {
                "id": "1",
                "category": "skills",
                "offerText": "FastAPI",
                "cvText": "FastAPI",
                "status": "match",
                "confidence": 0.9,
            }
        ],
        summary={
            "totalItems": 1,
            "matches": 1,
            "missing": 0,
            "unclear": 0,
            "matchPercentage": 100,
        },
    )
    db_session.add(record)
    db_session.commit()
    db_session.refresh(record)

    listing = client.get("/api/comparisons", headers=auth_headers)
    assert listing.status_code == 200
    payload = listing.json()
    assert payload["total"] == 1
    assert payload["items"][0]["id"] == str(record.id)
    assert payload["items"][0]["match_percentage"] == 100

    detail = client.get(f"/api/comparisons/{record.id}", headers=auth_headers)
    assert detail.status_code == 200
    body = detail.json()
    assert body["offer_text"].startswith("Développeur Python")
    assert len(body["items"]) == 1

    deleted = client.delete(f"/api/comparisons/{record.id}", headers=auth_headers)
    assert deleted.status_code == 200
    assert deleted.json()["success"] is True

    missing = client.get(f"/api/comparisons/{record.id}", headers=auth_headers)
    assert missing.status_code == 404


def test_comparisons_require_auth(client):
    response = client.get("/api/comparisons")
    assert response.status_code in (401, 403)
