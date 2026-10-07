import json
import uuid
from unittest.mock import patch
from uuid import UUID

import pytest
from sqlalchemy import select

from app.models.comparison_record import ComparisonRecord
from app.services.comparison_diff import pair_items

COMPARE = "app.services.comparison_service.ai_service.compare_offer_and_cv"
OFFER = "Développeur Python senior — FastAPI, Postgres, Docker"


def _item(category, offer_text, status):
    return {"id": offer_text, "category": category, "offerText": offer_text, "status": status, "confidence": 0.9}


def _result(*items):
    matches = sum(item["status"] == "match" for item in items)
    missing = sum(item["status"] == "missing" for item in items)
    return {
        "items": list(items),
        "summary": {
            "totalItems": len(items),
            "matches": matches,
            "missing": missing,
            "unclear": len(items) - matches - missing,
            "matchPercentage": matches / len(items),
        },
    }


def _record(db_session, user_id, result, *, offer=OFFER, parent=None, offer_url=None):
    record = ComparisonRecord.from_analysis(
        user_id=UUID(str(user_id)),
        offer_text=offer,
        cv_text="CV",
        offer_url=offer_url,
        parent_comparison_id=parent.id if parent else None,
        **result,
    )
    db_session.add(record)
    db_session.commit()
    db_session.refresh(record)
    return record


def _user_id(registered_user):
    return registered_user["user"]["id"]


def _other_headers(client):
    email = f"other-{uuid.uuid4().hex[:8]}@example.com"
    response = client.post("/api/auth/register", json={"email": email, "password": "password123"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _stream(client, headers, **body):
    payload = {"offer_text": OFFER, "cv_text": "CV v2", **body}
    with client.stream("POST", "/api/compare-stream", headers=headers, json=payload) as response:
        text = "".join(response.iter_text())
        return response.status_code, [json.loads(line[6:]) for line in text.splitlines() if line.startswith("data: ")]


# --- Appariement des items ----------------------------------------------------


def test_pair_items_exact_then_fuzzy_within_category():
    before = [
        _item("skills", "FastAPI", "missing"),
        _item("skills", "Maîtrise de PostgreSQL en production", "unclear"),
        _item("experience", "5 ans d'expérience", "match"),
        _item("skills", "Kubernetes", "missing"),
    ]
    after = [
        _item("Skills", "fastapi", "match"),  # casse et accents ignorés
        _item("skills", "Bonne maîtrise de PostgreSQL en production", "match"),  # reformulation légère
        _item("experience", "5 ans d'expérience", "match"),
        _item("skills", "Terraform", "missing"),
    ]

    pairs, removed, added = pair_items(before, after)

    assert [(old["offerText"], new["offerText"]) for old, new in pairs] == [
        ("FastAPI", "fastapi"),
        ("5 ans d'expérience", "5 ans d'expérience"),
        ("Maîtrise de PostgreSQL en production", "Bonne maîtrise de PostgreSQL en production"),
    ]
    assert [item["offerText"] for item in removed] == ["Kubernetes"]
    assert [item["offerText"] for item in added] == ["Terraform"]


def test_pair_items_does_not_cross_categories():
    pairs, removed, added = pair_items([_item("skills", "Python", "match")], [_item("tools", "Python", "match")])
    assert pairs == []
    assert len(removed) == len(added) == 1


# --- Diff ---------------------------------------------------------------------


def test_diff_reports_score_delta_improvements_and_regressions(client, auth_headers, db_session, registered_user):
    before = _record(
        db_session,
        _user_id(registered_user),
        _result(_item("skills", "FastAPI", "missing"), _item("skills", "Docker", "match"), _item("skills", "SQL", "unclear")),
    )
    after = _record(
        db_session,
        _user_id(registered_user),
        _result(_item("skills", "FastAPI", "match"), _item("skills", "Docker", "unclear"), _item("skills", "SQL", "match")),
        parent=before,
    )

    response = client.get(f"/api/comparisons/{before.id}/diff/{after.id}", headers=auth_headers)

    assert response.status_code == 200
    diff = response.json()
    assert diff["before"]["id"] == str(before.id)
    assert diff["after"]["id"] == str(after.id)
    assert diff["score_delta"] == pytest.approx(1 / 3)
    assert diff["same_offer"] is True
    assert [(c["offerText"], c["before"], c["after"]) for c in diff["improved"]] == [
        ("FastAPI", "missing", "match"),
        ("SQL", "unclear", "match"),
    ]
    assert [(c["offerText"], c["before"], c["after"]) for c in diff["regressed"]] == [("Docker", "match", "unclear")]
    assert diff["unchanged"] == 0


def test_diff_requires_ownership_of_both_comparisons(client, auth_headers, db_session, registered_user):
    mine = _record(db_session, _user_id(registered_user), _result(_item("skills", "Python", "match")))
    other_headers = _other_headers(client)
    other_id = client.get("/api/auth/me", headers=other_headers).json()["id"]
    theirs = _record(db_session, other_id, _result(_item("skills", "Python", "missing")))

    for path in (f"/api/comparisons/{mine.id}/diff/{theirs.id}", f"/api/comparisons/{theirs.id}/diff/{mine.id}"):
        response = client.get(path, headers=auth_headers)
        assert response.status_code == 404
        assert response.json()["code"] == "history.comparison_not_found"

    assert client.get(f"/api/comparisons/{mine.id}/diff/{uuid.uuid4()}", headers=auth_headers).status_code == 404
    assert client.get(f"/api/comparisons/{mine.id}/diff/{mine.id}").status_code in (401, 403)


# --- Réanalyse via le flux ----------------------------------------------------


def test_rescore_links_parent_and_keeps_its_offer(client, auth_headers, db_session, registered_user):
    parent = _record(
        db_session,
        _user_id(registered_user),
        _result(_item("skills", "FastAPI", "missing")),
        offer_url="https://jobs.example.com/42",
    )

    with patch(COMPARE, return_value=_result(_item("skills", "FastAPI", "match"))) as compare:
        status, events = _stream(
            client, auth_headers, offer_text="offre modifiée", parent_comparison_id=str(parent.id)
        )

    assert status == 200
    assert compare.call_args.args[0] == OFFER  # offre de la version précédente, pas celle envoyée
    complete = events[-1]
    assert complete["type"] == "complete"
    child = db_session.get(ComparisonRecord, UUID(complete["comparison_id"]))
    assert child.parent_comparison_id == parent.id
    assert child.offer_text == OFFER
    assert child.offer_url == "https://jobs.example.com/42"
    assert child.cv_text == "CV v2"


def test_rescore_rejects_parent_of_another_user(client, auth_headers, db_session):
    other_headers = _other_headers(client)
    other_id = client.get("/api/auth/me", headers=other_headers).json()["id"]
    theirs = _record(db_session, other_id, _result(_item("skills", "Python", "match")))

    with patch(COMPARE) as compare:
        response = client.post(
            "/api/compare-stream",
            headers=auth_headers,
            json={"offer_text": OFFER, "cv_text": "CV", "parent_comparison_id": str(theirs.id)},
        )

    assert response.status_code == 404
    assert response.json()["code"] == "history.comparison_not_found"
    compare.assert_not_called()
    assert db_session.scalars(select(ComparisonRecord).where(ComparisonRecord.parent_comparison_id == theirs.id)).all() == []


def test_new_analysis_returns_its_id_without_parent(client, auth_headers, db_session):
    with patch(COMPARE, return_value=_result(_item("skills", "Python", "match"))):
        _, events = _stream(client, auth_headers)

    record = db_session.get(ComparisonRecord, UUID(events[-1]["comparison_id"]))
    assert record.parent_comparison_id is None


# --- Fil de versions dans l'historique ----------------------------------------


def test_listing_groups_versions_in_threads(client, auth_headers, db_session, registered_user):
    user_id = _user_id(registered_user)
    v1 = _record(db_session, user_id, _result(_item("skills", "Python", "missing")))
    v2 = _record(db_session, user_id, _result(_item("skills", "Python", "unclear")), parent=v1)
    v3 = _record(db_session, user_id, _result(_item("skills", "Python", "match")), parent=v2)
    alone = _record(db_session, user_id, _result(_item("skills", "Go", "match")), offer="Développeur Go")

    items = {item["id"]: item for item in client.get("/api/comparisons", headers=auth_headers).json()["items"]}

    for version, record in enumerate((v1, v2, v3), start=1):
        assert items[str(record.id)]["thread_id"] == str(v1.id)
        assert items[str(record.id)]["version"] == version
        assert items[str(record.id)]["thread_size"] == 3
    assert items[str(v2.id)]["parent_comparison_id"] == str(v1.id)
    assert (items[str(alone.id)]["thread_id"], items[str(alone.id)]["thread_size"]) == (str(alone.id), 1)


def test_deleting_a_middle_version_keeps_the_thread(client, auth_headers, db_session, registered_user):
    user_id = _user_id(registered_user)
    v1 = _record(db_session, user_id, _result(_item("skills", "Python", "missing")))
    v2 = _record(db_session, user_id, _result(_item("skills", "Python", "unclear")), parent=v1)
    v3 = _record(db_session, user_id, _result(_item("skills", "Python", "match")), parent=v2)

    assert client.delete(f"/api/comparisons/{v2.id}", headers=auth_headers).status_code == 200

    db_session.expire_all()
    assert db_session.get(ComparisonRecord, v3.id).parent_comparison_id == v1.id
    items = {item["id"]: item for item in client.get("/api/comparisons", headers=auth_headers).json()["items"]}
    assert (items[str(v3.id)]["thread_id"], items[str(v3.id)]["version"]) == (str(v1.id), 2)
