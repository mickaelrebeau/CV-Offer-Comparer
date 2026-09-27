from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


def _normalize_database_url(url: str) -> str:
    """Adapte l'URL Railway (postgresql://) au driver SQLAlchemy."""
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg://", 1)
    elif url.startswith("postgresql://") and "+psycopg" not in url:
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


if not settings.DATABASE_URL:
    raise RuntimeError("DATABASE_URL est requis (PostgreSQL Railway)")

engine = create_engine(
    _normalize_database_url(settings.DATABASE_URL),
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Crée les tables manquantes au démarrage."""
    from app.models.auth_token import AuthToken  # noqa: F401
    from app.models.comparison_record import ComparisonRecord  # noqa: F401
    from app.models.cover_letter_record import CoverLetterRecord  # noqa: F401
    from app.models.interview_record import InterviewRecord  # noqa: F401
    from app.models.llm_credential import UserLLMCredential  # noqa: F401
    from app.models.user import User  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _migrate_email_verification()
    _migrate_password_changed_at()


def _migrate_email_verification() -> None:
    """Ajoute users.email_verified_at (create_all ne modifie pas les tables existantes).

    Les comptes créés avant la vérification e-mail sont considérés comme vérifiés.
    """
    columns = {c["name"] for c in inspect(engine).get_columns("users")}
    if "email_verified_at" in columns:
        return
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified_at TIMESTAMPTZ"))
        conn.execute(text("UPDATE users SET email_verified_at = created_at WHERE email_verified_at IS NULL"))


def _migrate_password_changed_at() -> None:
    """Ajoute users.password_changed_at, vide pour les comptes existants (aucune session invalidée)."""
    columns = {c["name"] for c in inspect(engine).get_columns("users")}
    if "password_changed_at" in columns:
        return
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS password_changed_at TIMESTAMPTZ"))
