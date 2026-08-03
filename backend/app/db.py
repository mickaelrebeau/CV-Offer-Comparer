from collections.abc import Generator

from sqlalchemy import create_engine
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
    from app.models.comparison_record import ComparisonRecord  # noqa: F401
    from app.models.user import User  # noqa: F401

    Base.metadata.create_all(bind=engine)
