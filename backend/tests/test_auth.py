def test_register_and_login(client):
    email = "new.user@example.com"
    password = "password123"

    register = client.post(
        "/api/auth/register",
        json={"email": email, "password": password},
    )
    assert register.status_code == 200
    body = register.json()
    assert body["token_type"] == "bearer"
    assert body["user"]["email"] == email
    assert body["access_token"]

    login = client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )
    assert login.status_code == 200
    assert login.json()["user"]["email"] == email


def test_register_rejects_short_password(client):
    response = client.post(
        "/api/auth/register",
        json={"email": "short@example.com", "password": "123"},
    )
    assert response.status_code == 422


def test_login_rejects_bad_credentials(client, registered_user):
    response = client.post(
        "/api/auth/login",
        json={"email": registered_user["email"], "password": "wrong-password"},
    )
    assert response.status_code == 401


def test_me_requires_valid_token(client, auth_headers):
    ok = client.get("/api/auth/me", headers=auth_headers)
    assert ok.status_code == 200
    assert "@" in ok.json()["email"]

    bad = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer not-a-valid-token"},
    )
    assert bad.status_code == 401


def test_me_without_token(client):
    response = client.get("/api/auth/me")
    assert response.status_code in (401, 403)
