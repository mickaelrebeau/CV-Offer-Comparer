import pytest

from app.config import settings
from app.services.rate_limit_service import RateLimiter

PDF = {"file": ("cv.txt", b"not a pdf", "text/plain")}


def _upload(client, headers, ip="1.1.1.1"):
    return client.post("/api/upload-cv", files=PDF, headers={**headers, "X-Real-IP": ip})


@pytest.fixture
def limits(monkeypatch):
    def apply(**values):
        for name, value in values.items():
            monkeypatch.setattr(settings, name, value)

    apply(
        RATE_LIMIT_ENABLED=True,
        RATE_LIMIT_USER_PER_MINUTE=100,
        RATE_LIMIT_IP_PER_MINUTE=100,
        DAILY_QUOTA_UPLOAD=100,
        CLIENT_IP_HEADER="X-Real-IP",
    )
    return apply


def test_user_per_minute_limit_returns_429_with_retry_after(client, auth_headers, limits):
    limits(RATE_LIMIT_USER_PER_MINUTE=2)
    assert _upload(client, auth_headers).status_code == 400  # passe le limiter, rejeté car non PDF
    assert _upload(client, auth_headers, ip="2.2.2.2").status_code == 400

    blocked = _upload(client, auth_headers, ip="3.3.3.3")
    assert blocked.status_code == 429
    assert 1 <= int(blocked.headers["retry-after"]) <= 60


def test_ip_per_minute_limit(client, auth_headers, limits):
    limits(RATE_LIMIT_IP_PER_MINUTE=1)
    assert _upload(client, auth_headers, ip="9.9.9.9").status_code == 400
    assert _upload(client, auth_headers, ip="9.9.9.9").status_code == 429
    assert _upload(client, auth_headers, ip="8.8.8.8").status_code == 400


def test_daily_quota_returns_429_until_midnight(client, auth_headers, limits):
    limits(DAILY_QUOTA_UPLOAD=1)
    assert _upload(client, auth_headers).status_code == 400

    blocked = _upload(client, auth_headers)
    assert blocked.status_code == 429
    assert "Quota journalier" in blocked.json()["detail"]
    assert 1 <= int(blocked.headers["retry-after"]) <= 24 * 3600


def test_zero_means_unlimited_and_flag_disables(client, auth_headers, limits):
    limits(RATE_LIMIT_USER_PER_MINUTE=0, DAILY_QUOTA_UPLOAD=0)
    for _ in range(5):
        assert _upload(client, auth_headers).status_code == 400

    limits(RATE_LIMIT_ENABLED=False, RATE_LIMIT_USER_PER_MINUTE=1)
    for _ in range(3):
        assert _upload(client, auth_headers).status_code == 400


def test_rate_limit_requires_auth(client, limits):
    assert client.post("/api/upload-cv", files=PDF).status_code in (401, 403)


@pytest.mark.parametrize(
    "method,path",
    [
        ("post", "/api/compare-stream"),
        ("post", "/api/interview/generate-questions"),
        ("post", "/api/interview/analyze-responses"),
        ("post", "/api/cover-letter"),
    ],
)
def test_gemini_routes_are_limited(client, auth_headers, limits, method, path):
    limits(RATE_LIMIT_USER_PER_MINUTE=1)
    getattr(client, method)(path, headers=auth_headers)  # 1er appel consommé (422 : corps vide)
    response = getattr(client, method)(path, headers=auth_headers)
    assert response.status_code == 429


def test_free_upload_is_ip_limited(client, limits):
    limits(RATE_LIMIT_IP_PER_MINUTE=1)
    headers = {"X-Real-IP": "5.5.5.5"}
    assert client.post("/api/free-upload-cv", files=PDF, headers=headers).status_code == 400
    assert client.post("/api/free-upload-cv", files=PDF, headers=headers).status_code == 429


def test_sliding_window_expires(monkeypatch):
    limiter = RateLimiter()
    clock = [1000.0]
    monkeypatch.setattr("app.services.rate_limit_service.time.monotonic", lambda: clock[0])
    assert limiter.hit_window("k", 1, 60) is None
    assert limiter.hit_window("k", 1, 60) == 60
    clock[0] += 30
    assert limiter.hit_window("k", 1, 60) == 30
    clock[0] += 31
    assert limiter.hit_window("k", 1, 60) is None
