def test_health_ok(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "features" in data


def test_api_branding(client):
    assert client.get("/api/health").json()["message"] == "Talento API"
    assert client.get("/openapi.json").json()["info"]["title"] == "Talento API"
