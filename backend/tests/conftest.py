import os
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

# Variables avant tout import de l'app (pydantic-settings lit l'env au chargement)
os.environ.setdefault("GOOGLE_API_KEY", "test-google-key")
os.environ.setdefault("SECRET_KEY", "ci-test-secret-key")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault(
    "DATABASE_URL",
    os.environ.get(
        "TEST_DATABASE_URL",
        "postgresql://test:test@localhost:5432/talento_test",
    ),
)

from app.db import Base, get_db, _normalize_database_url  # noqa: E402
from app.main import app  # noqa: E402
from app.models.comparison_record import ComparisonRecord  # noqa: F401,E402
from app.models.interview_record import InterviewRecord  # noqa: F401,E402
from app.models.user import User  # noqa: F401,E402


TEST_DATABASE_URL = _normalize_database_url(os.environ["DATABASE_URL"])


@pytest.fixture(scope="session")
def engine():
    eng = create_engine(TEST_DATABASE_URL, poolclass=NullPool, pool_pre_ping=True)
    try:
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:  # pragma: no cover
        pytest.exit(f"PostgreSQL de test indisponible: {exc}", returncode=1)
    yield eng
    eng.dispose()


@pytest.fixture
def db_session(engine):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def registered_user(client):
    email = f"user-{uuid.uuid4().hex[:10]}@example.com"
    password = "password123"
    response = client.post(
        "/api/auth/register",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    return {
        "email": email,
        "password": password,
        "token": payload["access_token"],
        "user": payload["user"],
    }


@pytest.fixture
def auth_headers(registered_user):
    return {"Authorization": f"Bearer {registered_user['token']}"}
