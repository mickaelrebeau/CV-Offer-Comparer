import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app

DEBUG_ROUTES = [
    ("post", "/api/reset-free-analysis"),
    ("get", "/api/free-analysis-stats"),
    ("get", "/api/test-stream"),
    ("get", "/api/interview/test"),
]


@pytest.fixture
def client():
    # Sans context manager : pas de lifespan, donc pas besoin de PostgreSQL
    return TestClient(app)


@pytest.mark.parametrize("method,path", DEBUG_ROUTES)
def test_debug_endpoints_hidden_by_default(client, monkeypatch, method, path):
    monkeypatch.setattr(settings, "ENABLE_DEBUG_ENDPOINTS", False)
    monkeypatch.setattr(settings, "ENVIRONMENT", "development")
    assert getattr(client, method)(path).status_code == 404


@pytest.mark.parametrize("method,path", DEBUG_ROUTES)
def test_debug_endpoints_hidden_in_production_even_if_enabled(client, monkeypatch, method, path):
    monkeypatch.setattr(settings, "ENABLE_DEBUG_ENDPOINTS", True)
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    assert getattr(client, method)(path).status_code == 404


def test_debug_endpoint_available_in_dev_when_enabled(client, monkeypatch):
    monkeypatch.setattr(settings, "ENABLE_DEBUG_ENDPOINTS", True)
    monkeypatch.setattr(settings, "ENVIRONMENT", "development")
    response = client.get("/api/interview/test")
    assert response.status_code == 200


def test_debug_endpoints_not_in_openapi(client):
    paths = client.get("/openapi.json").json()["paths"]
    for _, path in DEBUG_ROUTES:
        assert path not in paths
