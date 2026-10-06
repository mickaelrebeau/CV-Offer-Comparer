import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.config import settings
from app.models.saved_cv import SavedCV
from app.services.saved_cv_service import MAX_CV_TEXT_CHARS

CV_TEXT = "Jane Doe\nDéveloppeuse front-end Vue.js — 5 ans d'expérience\nTypeScript, Pinia, Vite"
EN = {"Accept-Language": "en"}


def _headers(user) -> dict:
    return {"Authorization": f"Bearer {user['token']}"}


def _create(client, headers, **body):
    payload = {"label": "CV Dev Front", "text": CV_TEXT, "source_filename": "cv-front.pdf", **body}
    return client.post("/api/cvs", headers=headers, json=payload)


def _second_user(client):
    email = f"other-{uuid.uuid4().hex[:8]}@example.com"
    response = client.post("/api/auth/register", json={"email": email, "password": "password123"})
    return {"token": response.json()["access_token"], "user": response.json()["user"]}


# --- Authentification -----------------------------------------------------------


@pytest.mark.parametrize(
    "method,path",
    [
        ("get", "/api/cvs"),
        ("post", "/api/cvs"),
        ("get", f"/api/cvs/{uuid.uuid4()}"),
        ("patch", f"/api/cvs/{uuid.uuid4()}"),
        ("delete", f"/api/cvs/{uuid.uuid4()}"),
        ("post", f"/api/cvs/{uuid.uuid4()}/default"),
    ],
)
def test_routes_require_auth(client, method, path):
    assert getattr(client, method)(path).status_code in (401, 403)


def test_unverified_user_can_manage_cvs(client, unverified_user):
    # Pas d'appel IA : la vérification d'e-mail n'est pas exigée
    assert _create(client, _headers(unverified_user)).status_code == 201


# --- CRUD -------------------------------------------------------------------------


def test_create_list_and_get(client, auth_headers):
    created = _create(client, auth_headers)
    assert created.status_code == 201
    cv = created.json()
    assert cv["label"] == "CV Dev Front"
    assert cv["text"] == CV_TEXT
    assert cv["source_filename"] == "cv-front.pdf"
    assert cv["char_count"] == len(CV_TEXT)

    listing = client.get("/api/cvs", headers=auth_headers).json()
    assert listing["limit"] == settings.MAX_SAVED_CVS
    assert listing["default_id"] == cv["id"]
    assert len(listing["items"]) == 1
    # Liste légère : extrait uniquement, pas le texte complet
    assert "text" not in listing["items"][0]
    assert listing["items"][0]["excerpt"].startswith("Jane Doe")

    detail = client.get(f"/api/cvs/{cv['id']}", headers=auth_headers).json()
    assert detail["text"] == CV_TEXT


def test_rename_and_replace(client, auth_headers):
    cv_id = _create(client, auth_headers).json()["id"]

    renamed = client.patch(f"/api/cvs/{cv_id}", headers=auth_headers, json={"label": "  CV   Lead  "})
    assert renamed.status_code == 200
    assert renamed.json()["label"] == "CV Lead"
    assert renamed.json()["text"] == CV_TEXT
    assert renamed.json()["source_filename"] == "cv-front.pdf"

    replaced = client.patch(
        f"/api/cvs/{cv_id}",
        headers=auth_headers,
        json={"text": "Nouveau CV Lead", "source_filename": "C:\\Users\\jane\\cv-lead.txt"},
    )
    assert replaced.status_code == 200
    assert replaced.json()["text"] == "Nouveau CV Lead"
    assert replaced.json()["source_filename"] == "cv-lead.txt"
    assert replaced.json()["label"] == "CV Lead"

    # Texte collé à la main : plus de fichier d'origine
    pasted = client.patch(f"/api/cvs/{cv_id}", headers=auth_headers, json={"text": "CV collé"})
    assert pasted.json()["source_filename"] is None


def test_delete(client, auth_headers, db_session):
    cv_id = _create(client, auth_headers).json()["id"]
    response = client.delete(f"/api/cvs/{cv_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["items"] == []
    assert db_session.scalar(select(SavedCV)) is None
    assert client.get(f"/api/cvs/{cv_id}", headers=auth_headers).status_code == 404


# --- Validation -----------------------------------------------------------------


@pytest.mark.parametrize(
    "body,status,code",
    [
        ({"text": "   "}, 400, "cvs.empty_text"),
        ({"text": "x" * (MAX_CV_TEXT_CHARS + 1)}, 413, "cvs.text_too_long"),
        ({"label": ""}, 400, "cvs.invalid_label"),
        ({"label": "x" * 81}, 400, "cvs.invalid_label"),
    ],
)
def test_validation(client, auth_headers, body, status, code):
    response = _create(client, auth_headers, **body)
    assert response.status_code == status
    assert response.json()["code"] == code


def test_text_at_limit_is_accepted(client, auth_headers):
    assert _create(client, auth_headers, text="x" * MAX_CV_TEXT_CHARS).status_code == 201


def test_patch_validates_too(client, auth_headers):
    cv_id = _create(client, auth_headers).json()["id"]
    assert client.patch(f"/api/cvs/{cv_id}", headers=auth_headers, json={"text": ""}).status_code == 400
    assert client.patch(f"/api/cvs/{cv_id}", headers=auth_headers, json={"label": " "}).status_code == 400


# --- Limite par compte ------------------------------------------------------------


def test_limit_per_account(client, auth_headers):
    for index in range(settings.MAX_SAVED_CVS):
        assert _create(client, auth_headers, label=f"CV {index}").status_code == 201

    response = _create(client, auth_headers, label="CV de trop")
    assert response.status_code == 409
    assert response.json()["code"] == "cvs.limit_reached"
    assert str(settings.MAX_SAVED_CVS) in response.json()["detail"]

    en = client.post("/api/cvs", headers={**auth_headers, **EN}, json={"label": "Extra", "text": CV_TEXT})
    assert en.json()["detail"].startswith("You have reached the limit")


def test_limit_frees_up_after_delete(client, auth_headers):
    ids = [_create(client, auth_headers, label=f"CV {i}").json()["id"] for i in range(settings.MAX_SAVED_CVS)]
    client.delete(f"/api/cvs/{ids[0]}", headers=auth_headers)
    assert _create(client, auth_headers, label="CV remplaçant").status_code == 201


# --- CV par défaut unique -------------------------------------------------------------


def _defaults(client, headers) -> list[str]:
    return [item["id"] for item in client.get("/api/cvs", headers=headers).json()["items"] if item["is_default"]]


def test_first_cv_is_default_and_next_ones_are_not(client, auth_headers):
    first = _create(client, auth_headers, label="Premier").json()
    second = _create(client, auth_headers, label="Second").json()
    assert first["is_default"] is True
    assert second["is_default"] is False
    assert _defaults(client, auth_headers) == [first["id"]]


def test_set_default_keeps_a_single_default(client, auth_headers):
    first = _create(client, auth_headers, label="Premier").json()
    second = _create(client, auth_headers, label="Second").json()

    response = client.post(f"/api/cvs/{second['id']}/default", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["default_id"] == second["id"]
    assert _defaults(client, auth_headers) == [second["id"]]

    # Idempotent
    client.post(f"/api/cvs/{second['id']}/default", headers=auth_headers)
    assert _defaults(client, auth_headers) == [second["id"]]

    third = _create(client, auth_headers, label="Troisième", is_default=True).json()
    assert third["is_default"] is True
    assert _defaults(client, auth_headers) == [third["id"]]
    assert first["id"] not in _defaults(client, auth_headers)


def test_deleting_default_promotes_another(client, auth_headers):
    first = _create(client, auth_headers, label="Premier").json()
    second = _create(client, auth_headers, label="Second").json()

    listing = client.delete(f"/api/cvs/{first['id']}", headers=auth_headers).json()
    assert listing["default_id"] == second["id"]


def test_database_rejects_two_defaults(client, auth_headers, db_session, registered_user):
    _create(client, auth_headers)
    db_session.add(
        SavedCV(user_id=uuid.UUID(registered_user["user"]["id"]), label="Doublon", text=CV_TEXT, is_default=True)
    )
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


# --- Isolation entre utilisateurs -----------------------------------------------------


def test_users_cannot_access_each_other_cvs(client, auth_headers):
    cv_id = _create(client, auth_headers).json()["id"]
    other = _headers(_second_user(client))

    assert client.get("/api/cvs", headers=other).json()["items"] == []
    for method, path, kwargs in [
        ("get", f"/api/cvs/{cv_id}", {}),
        ("patch", f"/api/cvs/{cv_id}", {"json": {"label": "Volé"}}),
        ("delete", f"/api/cvs/{cv_id}", {}),
        ("post", f"/api/cvs/{cv_id}/default", {}),
    ]:
        response = getattr(client, method)(path, headers=other, **kwargs)
        assert response.status_code == 404, (method, path)
        assert response.json()["code"] == "cvs.not_found"

    # Intact pour son propriétaire
    cv = client.get(f"/api/cvs/{cv_id}", headers=auth_headers).json()
    assert cv["label"] == "CV Dev Front"
    assert cv["is_default"] is True


def test_limit_and_default_are_per_user(client, auth_headers):
    for index in range(settings.MAX_SAVED_CVS):
        _create(client, auth_headers, label=f"CV {index}")
    other = _headers(_second_user(client))
    created = _create(client, other, label="CV autre compte")
    assert created.status_code == 201
    assert created.json()["is_default"] is True


# --- Suppression du compte ------------------------------------------------------------


def test_account_deletion_cascades(client, auth_headers, db_session):
    _create(client, auth_headers, label="Premier")
    _create(client, auth_headers, label="Second")
    other = _headers(_second_user(client))
    _create(client, other, label="CV autre compte")

    assert client.delete("/api/auth/me", headers=auth_headers).status_code == 200
    db_session.expire_all()
    remaining = db_session.scalars(select(SavedCV)).all()
    assert [cv.label for cv in remaining] == ["CV autre compte"]
