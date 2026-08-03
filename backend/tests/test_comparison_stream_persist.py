from unittest.mock import patch
from uuid import UUID

from sqlalchemy import select

from app.models.comparison_record import ComparisonRecord


FAKE_RESULT = {
    "items": [
        {
            "id": "skill-1",
            "category": "skills",
            "offerText": "Python",
            "cvText": "Python",
            "status": "match",
            "confidence": 0.95,
        }
    ],
    "summary": {
        "totalItems": 1,
        "matches": 1,
        "missing": 0,
        "unclear": 0,
        "matchPercentage": 100.0,
        "categoryStats": {},
    },
}


def test_compare_stream_persists_history(client, auth_headers, db_session, registered_user):
    with patch(
        "app.services.comparison_service.ai_service.compare_offer_and_cv",
        return_value=FAKE_RESULT,
    ):
        with client.stream(
            "POST",
            "/api/compare-stream",
            headers={**auth_headers, "Accept": "text/event-stream"},
            json={
                "offer_text": "Offre Python FastAPI",
                "cv_text": "CV développeur Python",
            },
        ) as response:
            assert response.status_code == 200
            body = "".join(response.iter_text())
            assert '"type": "complete"' in body or '"type":"complete"' in body

    user_id = UUID(registered_user["user"]["id"])
    db_session.expire_all()
    rows = db_session.scalars(
        select(ComparisonRecord).where(ComparisonRecord.user_id == user_id)
    ).all()
    assert len(rows) == 1
    assert rows[0].match_percentage == 100.0
    assert rows[0].total_items == 1
