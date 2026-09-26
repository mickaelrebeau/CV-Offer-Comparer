from urllib.parse import parse_qs, urlparse

import pytest

from app.config import settings
from app.routers import auth as auth_router
from app.services.oauth_service import OAUTH_STATE_COOKIE
from app.services.redis_service import redis_service

GOOGLE_PROFILE = {
    "sub": "google-123",
    "email": "google.user@example.com",
    "name": "Google User",
    "picture": "https://example.com/avatar.png",
}


@pytest.fixture(autouse=True)
def google_config(monkeypatch):
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_ID", "client-id")
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_SECRET", "client-secret")
    monkeypatch.setattr(settings, "GOOGLE_REDIRECT_URI", "http://testserver/api/auth/google/callback")
    monkeypatch.setattr(settings, "FRONTEND_URL", "http://front.test")
    # Codes OAuth en mémoire : ne jamais écrire dans le Redis du .env
    monkeypatch.setattr(redis_service, "redis_available", False)

    async def fake_exchange(code: str):
        assert code == "google-code"
        return GOOGLE_PROFILE

    monkeypatch.setattr(auth_router, "exchange_google_code", fake_exchange)


def _query(response) -> dict[str, str]:
    location = response.headers["location"]
    return {k: v[0] for k, v in parse_qs(urlparse(location).query).items()}


def _start_login(client) -> str:
    response = client.get("/api/auth/google", follow_redirects=False)
    assert response.status_code == 302
    state = _query(response)["state"]
    assert client.cookies.get(OAUTH_STATE_COOKIE) == state
    return state


def _callback(client, **params):
    return client.get("/api/auth/google/callback", params=params, follow_redirects=False)


def test_google_login_sets_state_cookie(client):
    response = client.get("/api/auth/google", follow_redirects=False)
    cookie = response.headers["set-cookie"].lower()
    assert "httponly" in cookie
    assert "samesite=lax" in cookie
    assert _query(response)["state"]


def test_callback_rejects_missing_state_cookie(client):
    response = _callback(client, code="google-code", state="forged")
    assert response.status_code == 302
    assert _query(response)["reason"] == "invalid_state"


def test_callback_rejects_mismatched_state(client):
    _start_login(client)
    response = _callback(client, code="google-code", state="forged")
    assert _query(response)["reason"] == "invalid_state"


def test_callback_redirects_with_one_time_code_not_jwt(client):
    state = _start_login(client)
    response = _callback(client, code="google-code", state=state)

    location = response.headers["location"]
    assert location.startswith("http://front.test/auth/callback?")
    query = _query(response)
    assert "token" not in query
    assert "." not in query["code"]  # pas un JWT
    assert OAUTH_STATE_COOKIE in response.headers["set-cookie"]  # cookie supprimé


def test_exchange_returns_jwt_once(client):
    state = _start_login(client)
    code = _query(_callback(client, code="google-code", state=state))["code"]

    first = client.post("/api/auth/google/exchange", json={"code": code})
    assert first.status_code == 200
    body = first.json()
    assert body["user"]["email"] == GOOGLE_PROFILE["email"]

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {body['access_token']}"})
    assert me.status_code == 200

    replay = client.post("/api/auth/google/exchange", json={"code": code})
    assert replay.status_code == 400


def test_exchange_rejects_unknown_code(client):
    response = client.post("/api/auth/google/exchange", json={"code": "unknown"})
    assert response.status_code == 400
