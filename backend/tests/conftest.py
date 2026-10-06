import os
import uuid
from datetime import datetime, timezone

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
from alembic import command  # noqa: E402

from app.main import app  # noqa: E402
from app.migrations import alembic_config  # noqa: E402
from app.models import tables  # noqa: F401,E402  (enregistre toutes les tables)
from app.models.user import User  # noqa: E402
from app.services.rate_limit_service import rate_limiter  # noqa: E402
from app.services.redis_service import redis_service  # noqa: E402


TEST_DATABASE_URL = _normalize_database_url(os.environ["DATABASE_URL"])


@pytest.fixture(autouse=True)
def isolated_rate_limits(monkeypatch):
    # Stockage mémoire : les tests n'écrivent jamais dans le Redis du .env
    monkeypatch.setattr(redis_service, "redis_available", False)
    rate_limiter.reset()
    yield
    rate_limiter.reset()


@pytest.fixture(autouse=True)
def sent_emails(monkeypatch):
    """Capture les e-mails au lieu de les envoyer."""
    outbox = []
    monkeypatch.setattr("app.routers.auth.send_email", outbox.append)
    return outbox


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


def reset_schema(engine) -> None:
    """Schéma vide (tables applicatives et version Alembic)."""
    Base.metadata.drop_all(bind=engine)
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS alembic_version"))


def create_schema(engine) -> None:
    """Tables des modèles, marquées à la dernière migration (le démarrage de l'app n'y touche plus)."""
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        command.stamp(alembic_config(conn), "head")


@pytest.fixture
def db_session(engine):
    reset_schema(engine)
    create_schema(engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        reset_schema(engine)


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


def _register(client):
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
def unverified_user(client):
    return _register(client)


@pytest.fixture
def registered_user(client, db_session):
    """Utilisateur à l'adresse vérifiée (accès aux fonctionnalités IA)."""
    data = _register(client)
    user = db_session.get(User, uuid.UUID(data["user"]["id"]))
    user.email_verified_at = datetime.now(timezone.utc)
    db_session.commit()
    return data


@pytest.fixture
def auth_headers(registered_user):
    return {"Authorization": f"Bearer {registered_user['token']}"}
