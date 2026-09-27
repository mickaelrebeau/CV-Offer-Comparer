import json
from types import SimpleNamespace
from uuid import UUID

import anthropic
import httpx
import httpx2
import pytest
from cryptography.fernet import Fernet
from google.genai import errors as genai_errors
from sqlalchemy import select

from app.config import settings
from app.models.llm_credential import UserLLMCredential
from app.services.ai_service import ai_service
from app.services.llm import clients, crypto
from app.services.llm.clients import OpenAICompatibleClient

OPENAI_KEY = "sk-test-openai-0123456789abcdef"
ANTHROPIC_KEY = "sk-ant-test-0123456789abcdef"
COMPARISON = {
    "items": [
        {
            "category": "compétences techniques",
            "offerText": "Python",
            "cvText": "Python",
            "status": "match",
            "confidence": 0.9,
            "suggestions": [],
        }
    ]
}
QUESTIONS = [{"text": "Parlez-moi de FastAPI ?", "category": "Compétences"}]


@pytest.fixture(autouse=True)
def byok(monkeypatch):
    monkeypatch.setattr(settings, "LLM_ENCRYPTION_KEYS", Fernet.generate_key().decode())
    monkeypatch.setattr(settings, "LLM_ALLOW_PRIVATE_BASE_URLS", False)
    # DNS sans réseau : tout hôte résout vers une IP publique, sauf override dans le test
    monkeypatch.setattr("app.services.llm.urls._resolve", lambda host: ["93.184.216.34"])


@pytest.fixture
def openai_calls(monkeypatch):
    """Faux serveur OpenAI-compatible : `responses` est une file de (statut, corps JSON)."""
    calls, responses = [], []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append({"url": str(request.url), "headers": request.headers, "json": json.loads(request.content)})
        status, body = responses.pop(0) if responses else (200, _completion({"ok": True}))
        return httpx.Response(status, json=body)

    monkeypatch.setattr(clients, "http_transport", httpx.MockTransport(handler))
    return SimpleNamespace(calls=calls, responses=responses)


@pytest.fixture
def platform_gemini(monkeypatch):
    """Gemini plateforme simulé ; `fail` : erreur API à lever."""
    state = SimpleNamespace(calls=0, fail=None, payload=COMPARISON)

    def generate_content(**kwargs):
        state.calls += 1
        if state.fail:
            raise state.fail
        return SimpleNamespace(text=json.dumps(state.payload))

    fake = SimpleNamespace(models=SimpleNamespace(generate_content=generate_content))
    monkeypatch.setattr(ai_service.llm, "_sdk", lambda: fake)
    return state


def _completion(payload) -> dict:
    return {"choices": [{"message": {"role": "assistant", "content": json.dumps(payload)}}]}


def _save(client, headers, **body):
    payload = {"provider": "openai", "api_key": OPENAI_KEY, "model": "gpt-4.1-mini", "verify": False, **body}
    return client.put("/api/profile/llm-credentials", headers=headers, json=payload)


def _rows(db_session, user=None):
    db_session.expire_all()
    query = select(UserLLMCredential)
    if user:
        query = query.where(UserLLMCredential.user_id == UUID(user["user"]["id"]))
    return db_session.scalars(query).all()


def _other_user_headers(client):
    other = client.post("/api/auth/register", json={"email": "other@example.com", "password": "password123"})
    return {"Authorization": f"Bearer {other.json()['access_token']}"}


def _sse(response) -> list[dict]:
    return [json.loads(line[6:]) for line in response.text.splitlines() if line.startswith("data: ")]


# --- Chiffrement ---------------------------------------------------------------


def test_encrypt_roundtrip_and_hint():
    token = crypto.encrypt(OPENAI_KEY)
    assert OPENAI_KEY not in token
    assert crypto.decrypt(token) == OPENAI_KEY
    assert crypto.key_hint(OPENAI_KEY) == "sk-••••cdef"
    assert crypto.key_hint("short") == "••••rt"


def test_key_rotation(monkeypatch):
    old = settings.LLM_ENCRYPTION_KEYS
    token = crypto.encrypt(OPENAI_KEY)
    monkeypatch.setattr(settings, "LLM_ENCRYPTION_KEYS", f"{Fernet.generate_key().decode()},{old}")
    rotated = crypto.rotate(token)
    monkeypatch.setattr(settings, "LLM_ENCRYPTION_KEYS", settings.LLM_ENCRYPTION_KEYS.split(",")[0])
    assert crypto.decrypt(rotated) == OPENAI_KEY
    with pytest.raises(Exception) as exc:
        crypto.decrypt(token)  # l'ancienne clé a été retirée
    assert exc.value.code == "llm.credential_unreadable"


# --- API : catalogue et credentials -------------------------------------------


def test_catalog(client, auth_headers):
    body = client.get("/api/profile/llm-providers", headers=auth_headers).json()
    ids = {p["id"] for p in body["providers"]}
    assert body["byok_enabled"] is True
    assert {"gemini", "openai", "anthropic", "deepseek", "qwen", "kimi", "openai_compatible"} <= ids
    compatible = next(p for p in body["providers"] if p["id"] == "openai_compatible")
    assert compatible["base_url_required"] is True


def test_endpoints_require_auth(client):
    assert client.get("/api/profile/llm-providers").status_code in (401, 403)
    assert client.get("/api/profile/llm-credentials").status_code in (401, 403)
    assert client.put("/api/profile/llm-credentials", json={}).status_code in (401, 403)


def test_save_never_returns_or_stores_key_in_clear(client, auth_headers, db_session, registered_user):
    response = _save(client, auth_headers)
    assert response.status_code == 200, response.text
    body = response.json()
    assert OPENAI_KEY not in response.text
    assert body["key_hint"] == "sk-••••cdef"
    assert body["is_active"] is True  # première configuration : active d'office

    listing = client.get("/api/profile/llm-credentials", headers=auth_headers)
    assert OPENAI_KEY not in listing.text
    assert listing.json()["active_id"] == body["id"]

    row = _rows(db_session, registered_user)[0]
    assert OPENAI_KEY not in row.encrypted_api_key
    assert crypto.decrypt(row.encrypted_api_key) == OPENAI_KEY


def test_update_keeps_existing_key_when_blank(client, auth_headers, db_session, registered_user):
    _save(client, auth_headers)
    response = _save(client, auth_headers, api_key="", model="gpt-4.1")
    assert response.status_code == 200
    assert response.json()["model"] == "gpt-4.1"
    rows = _rows(db_session, registered_user)
    assert len(rows) == 1  # une configuration par provider
    assert crypto.decrypt(rows[0].encrypted_api_key) == OPENAI_KEY


@pytest.mark.parametrize(
    "body,code",
    [
        ({"provider": "mistral"}, "llm.unsupported_provider"),
        ({"api_key": ""}, "llm.api_key_required"),
        ({"api_key": "sk bad key"}, "llm.invalid_api_key_format"),
        ({"model": "gpt 4; drop"}, "llm.invalid_model"),
        ({"provider": "openai_compatible", "model": "llama"}, "llm.base_url_required"),
        ({"provider": "gemini", "base_url": "https://proxy.example.com"}, "llm.invalid_base_url"),
        ({"base_url": "http://api.example.com/v1"}, "llm.invalid_base_url"),
        ({"base_url": "https://user:pass@api.example.com/v1"}, "llm.invalid_base_url"),
        ({"base_url": "https://localhost/v1"}, "llm.invalid_base_url"),
        ({"base_url": "https://metadata.internal/v1"}, "llm.invalid_base_url"),
    ],
)
def test_save_validation(client, auth_headers, db_session, body, code):
    response = _save(client, auth_headers, **body)
    assert response.status_code == 400, response.text
    assert response.json()["code"] == code
    assert _rows(db_session) == []


@pytest.mark.parametrize("address", ["127.0.0.1", "10.0.0.5", "169.254.169.254", "192.168.1.10", "::1", "fd00::1"])
def test_base_url_resolving_to_private_ip_is_rejected(client, auth_headers, monkeypatch, address):
    monkeypatch.setattr("app.services.llm.urls._resolve", lambda host: [address])
    response = _save(client, auth_headers, provider="openai_compatible", base_url="https://llm.example.com/v1")
    assert response.json()["code"] == "llm.invalid_base_url"


def test_private_base_url_allowed_in_dev_only(client, auth_headers, monkeypatch):
    monkeypatch.setattr(settings, "LLM_ALLOW_PRIVATE_BASE_URLS", True)
    monkeypatch.setattr(settings, "ENVIRONMENT", "development")
    ollama = {"provider": "openai_compatible", "base_url": "http://localhost:11434/v1", "model": "llama3"}
    assert _save(client, auth_headers, **ollama).status_code == 200

    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    assert _save(client, auth_headers, **ollama).json()["code"] == "llm.invalid_base_url"


def test_one_active_credential_at_a_time(client, auth_headers, db_session, registered_user):
    openai_id = _save(client, auth_headers).json()["id"]
    deepseek = _save(client, auth_headers, provider="deepseek", model="deepseek-chat", activate=False).json()
    assert deepseek["is_active"] is False

    listing = client.post(f"/api/profile/llm-credentials/{deepseek['id']}/activate", headers=auth_headers).json()
    assert listing["active_id"] == deepseek["id"]
    assert {item["id"]: item["is_active"] for item in listing["items"]} == {openai_id: False, deepseek["id"]: True}

    listing = client.post("/api/profile/llm-credentials/deactivate", headers=auth_headers).json()
    assert listing["active_id"] is None
    assert not any(row.is_active for row in _rows(db_session, registered_user))


def test_delete_purges_credential(client, auth_headers, db_session):
    credential_id = _save(client, auth_headers).json()["id"]
    listing = client.delete(f"/api/profile/llm-credentials/{credential_id}", headers=auth_headers).json()
    assert listing == {"items": [], "active_id": None}
    assert _rows(db_session) == []


def test_credentials_are_isolated_between_users(client, auth_headers, db_session):
    credential_id = _save(client, auth_headers).json()["id"]
    other = _other_user_headers(client)

    assert client.get("/api/profile/llm-credentials", headers=other).json()["items"] == []
    for method, path in (
        ("post", f"/api/profile/llm-credentials/{credential_id}/activate"),
        ("delete", f"/api/profile/llm-credentials/{credential_id}"),
    ):
        response = getattr(client, method)(path, headers=other)
        assert response.status_code == 404
        assert response.json()["code"] == "llm.credential_not_found"
    assert len(_rows(db_session)) == 1


def test_byok_disabled_without_encryption_key(client, auth_headers, monkeypatch):
    monkeypatch.setattr(settings, "LLM_ENCRYPTION_KEYS", "")
    assert client.get("/api/profile/llm-providers", headers=auth_headers).json()["byok_enabled"] is False
    response = _save(client, auth_headers)
    assert response.status_code == 503
    assert response.json()["code"] == "llm.byok_disabled"


def test_account_deletion_purges_credentials(client, auth_headers, db_session):
    _save(client, auth_headers)
    assert client.delete("/api/auth/me", headers=auth_headers).status_code == 200
    assert _rows(db_session) == []


# --- Vérification de la clé ----------------------------------------------------


def test_verify_calls_provider_before_saving(client, auth_headers, openai_calls):
    response = _save(client, auth_headers, verify=True)
    assert response.status_code == 200
    call = openai_calls.calls[0]
    assert call["url"] == "https://api.openai.com/v1/chat/completions"
    assert call["headers"]["authorization"] == f"Bearer {OPENAI_KEY}"
    assert call["json"]["model"] == "gpt-4.1-mini"
    assert call["json"]["response_format"] == {"type": "json_object"}


def test_verify_rejects_invalid_key_without_saving_or_logging_it(client, auth_headers, db_session, openai_calls, capsys):
    openai_calls.responses.append((401, {"error": {"message": "Incorrect API key provided", "code": "invalid_api_key"}}))
    response = _save(client, auth_headers, verify=True)

    assert response.status_code == 400
    assert response.json()["code"] == "llm.invalid_user_api_key"
    assert OPENAI_KEY not in response.text
    assert OPENAI_KEY not in capsys.readouterr().out
    assert _rows(db_session) == []


def test_verify_rate_limited(client, auth_headers, monkeypatch):
    monkeypatch.setattr(settings, "RATE_LIMIT_ENABLED", True)
    monkeypatch.setattr(settings, "RATE_LIMIT_USER_PER_MINUTE", 100)
    monkeypatch.setattr(settings, "DAILY_QUOTA_LLM_CREDENTIALS", 1)
    assert _save(client, auth_headers).status_code == 200
    blocked = _save(client, auth_headers)
    assert blocked.status_code == 429
    assert blocked.json()["code"] == "rate.daily_quota"


# --- Routage des appels IA -------------------------------------------------------


def test_compare_uses_platform_without_byok(client, auth_headers, platform_gemini, openai_calls):
    response = client.post("/api/compare-stream", headers=auth_headers, json={"offer_text": "Python", "cv_text": "Python"})
    assert any(event["type"] == "complete" for event in _sse(response))
    assert platform_gemini.calls == 1
    assert openai_calls.calls == []


def test_compare_uses_active_openai_compatible_provider(client, auth_headers, platform_gemini, openai_calls):
    _save(client, auth_headers, provider="openai_compatible", base_url="https://llm.example.com/v1/", model="llama-3.3")
    openai_calls.responses.append((200, _completion(COMPARISON)))

    response = client.post("/api/compare-stream", headers=auth_headers, json={"offer_text": "Python", "cv_text": "Python"})
    events = _sse(response)
    assert any(event["type"] == "complete" for event in events)
    assert platform_gemini.calls == 0
    call = openai_calls.calls[0]
    assert call["url"] == "https://llm.example.com/v1/chat/completions"
    assert call["json"]["model"] == "llama-3.3"
    assert "response_format" not in call["json"]  # endpoint libre : JSON demandé par le prompt


def test_back_to_platform_after_deactivation(client, auth_headers, platform_gemini, openai_calls):
    _save(client, auth_headers)
    client.post("/api/profile/llm-credentials/deactivate", headers=auth_headers)
    client.post("/api/compare-stream", headers=auth_headers, json={"offer_text": "Python", "cv_text": "Python"})
    assert platform_gemini.calls == 1
    assert openai_calls.calls == []


def test_openai_retries_without_unsupported_temperature(client, auth_headers, openai_calls):
    _save(client, auth_headers, model="gpt-5-mini")
    openai_calls.responses.extend(
        [
            (400, {"error": {"message": "Unsupported value: 'temperature' does not support 0.4"}}),
            (200, _completion(QUESTIONS)),
        ]
    )
    files = {"cv_file": ("cv.txt", b"Python FastAPI", "text/plain")}
    response = client.post(
        "/api/interview/generate-questions", headers=auth_headers, files=files, data={"job_text": "Dev Python", "num_questions": 1}
    )
    assert response.status_code == 200, response.text
    assert response.json()["interview_session"]["questions"] == QUESTIONS
    assert "temperature" in openai_calls.calls[0]["json"]
    assert "temperature" not in openai_calls.calls[1]["json"]


def test_interview_uses_active_anthropic_provider(client, auth_headers, platform_gemini, monkeypatch):
    seen = {}

    class FakeAnthropic:
        def __init__(self, **kwargs):
            seen["client"] = kwargs
            self.messages = SimpleNamespace(create=self.create)

        def create(self, **kwargs):
            seen["request"] = kwargs
            return SimpleNamespace(
                stop_reason="end_turn",
                content=[SimpleNamespace(type="thinking", thinking=""), SimpleNamespace(type="text", text=json.dumps(QUESTIONS))],
            )

    monkeypatch.setattr("app.services.llm.clients.anthropic.Anthropic", FakeAnthropic)
    _save(client, auth_headers, provider="anthropic", api_key=ANTHROPIC_KEY, model="claude-sonnet-5")

    files = {"cv_file": ("cv.txt", b"Python FastAPI", "text/plain")}
    response = client.post(
        "/api/interview/generate-questions", headers=auth_headers, files=files, data={"job_text": "Dev Python", "num_questions": 1}
    )
    assert response.status_code == 200, response.text
    assert response.json()["interview_session"]["questions"] == QUESTIONS
    assert seen["client"]["api_key"] == ANTHROPIC_KEY
    assert seen["request"]["model"] == "claude-sonnet-5"
    assert "temperature" not in seen["request"]
    assert platform_gemini.calls == 0


# --- Erreurs normalisées ----------------------------------------------------------


def test_platform_quota_is_reported_in_stream(client, auth_headers, platform_gemini):
    platform_gemini.fail = genai_errors.ClientError(
        429, {"error": {"code": 429, "message": "Quota exceeded", "status": "RESOURCE_EXHAUSTED"}}
    )
    response = client.post(
        "/api/compare-stream",
        headers={**auth_headers, "Accept-Language": "en"},
        json={"offer_text": "Python", "cv_text": "Python"},
    )
    error = next(event for event in _sse(response) if event["type"] == "error")
    assert error["code"] == "llm.platform_quota_exceeded"
    assert error["message"].startswith("Talento's AI quota is exhausted")


def test_platform_quota_is_not_masked_by_interview_fallback(client, auth_headers, platform_gemini):
    platform_gemini.fail = genai_errors.ClientError(429, {"error": {"code": 429, "message": "Quota", "status": "RESOURCE_EXHAUSTED"}})
    files = {"cv_file": ("cv.txt", b"Python", "text/plain")}
    response = client.post("/api/interview/generate-questions", headers=auth_headers, files=files, data={"job_text": "Dev"})
    assert response.status_code == 503
    assert response.json()["code"] == "llm.platform_quota_exceeded"


def test_user_provider_quota_is_distinct_from_platform(client, auth_headers, openai_calls):
    _save(client, auth_headers)
    openai_calls.responses.append((429, {"error": {"message": "You exceeded your current quota", "code": "insufficient_quota"}}))
    response = client.post("/api/compare-stream", headers=auth_headers, json={"offer_text": "Python", "cv_text": "Python"})
    error = next(event for event in _sse(response) if event["type"] == "error")
    assert error["code"] == "llm.user_provider_quota_exceeded"


def test_cover_letter_reports_invalid_user_key(client, auth_headers, openai_calls):
    _save(client, auth_headers)
    openai_calls.responses.append((401, {"error": {"message": "invalid"}}))
    response = client.post("/api/cover-letter", headers=auth_headers, data={"job_text": "Dev Python", "cv_text": "Python"})
    error = next(event for event in _sse(response) if event["type"] == "error")
    assert error["code"] == "llm.invalid_user_api_key"


def test_unreadable_credential_asks_to_save_key_again(client, auth_headers, monkeypatch):
    _save(client, auth_headers)
    monkeypatch.setattr(settings, "LLM_ENCRYPTION_KEYS", Fernet.generate_key().decode())
    response = client.post("/api/compare-stream", headers=auth_headers, json={"offer_text": "Python", "cv_text": "Python"})
    assert response.status_code == 409
    assert response.json()["code"] == "llm.credential_unreadable"


@pytest.mark.parametrize(
    "error,code",
    [
        (anthropic.AuthenticationError, "llm.invalid_user_api_key"),
        (anthropic.RateLimitError, "llm.user_provider_quota_exceeded"),
        (anthropic.InternalServerError, "llm.provider_unavailable"),
        (anthropic.NotFoundError, "llm.provider_rejected"),
    ],
)
def test_anthropic_errors_are_normalized(monkeypatch, error, code):
    status = {"AuthenticationError": 401, "RateLimitError": 429, "InternalServerError": 500, "NotFoundError": 404}[error.__name__]
    request = httpx2.Request("POST", "https://api.anthropic.com/v1/messages")
    exc = error("failure", response=httpx2.Response(status, request=request), body=None)

    class FailingAnthropic:
        def __init__(self, **kwargs):
            self.messages = SimpleNamespace(create=lambda **kw: (_ for _ in ()).throw(exc))

    monkeypatch.setattr("app.services.llm.clients.anthropic.Anthropic", FailingAnthropic)
    llm = clients.AnthropicClient(api_key=ANTHROPIC_KEY, model="claude-opus-5", base_url=None, custom_base_url=False)
    with pytest.raises(Exception) as raised:
        llm.generate_json("{}")
    assert raised.value.code == code


def test_anthropic_refusal(monkeypatch):
    class Refusing:
        def __init__(self, **kwargs):
            self.messages = SimpleNamespace(create=lambda **kw: SimpleNamespace(stop_reason="refusal", content=[]))

    monkeypatch.setattr("app.services.llm.clients.anthropic.Anthropic", Refusing)
    llm = clients.AnthropicClient(api_key=ANTHROPIC_KEY, model="claude-opus-5", base_url=None, custom_base_url=False)
    with pytest.raises(Exception) as raised:
        llm.generate_json("{}")
    assert raised.value.code == "llm.provider_refused"


def test_openai_compatible_revalidates_base_url_at_call_time(monkeypatch, openai_calls):
    llm = OpenAICompatibleClient(
        provider="openai_compatible",
        api_key=OPENAI_KEY,
        model="llama",
        base_url="https://llm.example.com/v1",
        custom_base_url=True,
        json_mode=False,
    )
    # Le DNS pointe désormais vers le réseau interne (rebinding)
    monkeypatch.setattr("app.services.llm.urls._resolve", lambda host: ["10.0.0.7"])
    with pytest.raises(Exception) as raised:
        llm.generate_json("{}")
    assert raised.value.detail and raised.value.code == "llm.invalid_base_url"
    assert openai_calls.calls == []
