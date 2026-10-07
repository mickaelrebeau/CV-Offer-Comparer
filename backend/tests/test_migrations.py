"""Migrations Alembic : schéma identique aux modèles, base existante d'avant Alembic, aller-retour."""

import uuid

import pytest
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import inspect, text

from app.db import Base
from app.migrations import BASELINE_REVISION, alembic_config, run_migrations
from tests.conftest import reset_schema


@pytest.fixture
def empty_db(engine):
    reset_schema(engine)
    yield engine
    reset_schema(engine)


def _head() -> str:
    return ScriptDirectory.from_config(alembic_config()).get_current_head()


def _current(engine) -> str | None:
    with engine.connect() as conn:
        return MigrationContext.configure(conn).get_current_revision()


def _schema_diff(engine) -> list:
    with engine.connect() as conn:
        context = MigrationContext.configure(conn, opts={"compare_type": True})
        return compare_metadata(context, Base.metadata)


def test_single_head():
    # Deux migrations parallèles (branches) doivent être fusionnées avant déploiement
    assert len(ScriptDirectory.from_config(alembic_config()).get_heads()) == 1


def test_fresh_database_matches_models(empty_db):
    run_migrations(empty_db)
    assert _current(empty_db) == _head()
    assert _schema_diff(empty_db) == []


def test_migrations_are_idempotent(empty_db):
    run_migrations(empty_db)
    run_migrations(empty_db)
    assert _current(empty_db) == _head()


def test_downgrade_to_base_and_back(empty_db):
    run_migrations(empty_db)
    with empty_db.begin() as conn:
        command.downgrade(alembic_config(conn), "base")
    tables = set(inspect(empty_db).get_table_names())
    assert tables <= {"alembic_version"}

    run_migrations(empty_db)
    assert _schema_diff(empty_db) == []


def test_each_migration_downgrades(empty_db):
    """Chaque révision s'annule proprement (head → précédente → head)."""
    run_migrations(empty_db)
    with empty_db.begin() as conn:
        command.downgrade(alembic_config(conn), "-1")
    run_migrations(empty_db)
    assert _schema_diff(empty_db) == []


def test_legacy_database_is_upgraded_and_stamped(empty_db):
    """Base de production créée par create_all avant Alembic (colonnes ad hoc absentes)."""
    _create_legacy_schema(empty_db)
    user_id = uuid.uuid4()
    with empty_db.begin() as conn:
        conn.execute(text("DROP TABLE saved_cvs"))
        conn.execute(text("ALTER TABLE users DROP COLUMN email_verified_at"))
        conn.execute(text("ALTER TABLE users DROP COLUMN password_changed_at"))
        conn.execute(text("INSERT INTO users (id, email) VALUES (:id, 'legacy@example.com')"), {"id": user_id})

    run_migrations(empty_db)

    assert _current(empty_db) == _head()
    assert _schema_diff(empty_db) == []
    with empty_db.connect() as conn:
        row = conn.execute(
            text("SELECT email_verified_at IS NOT NULL, password_changed_at FROM users WHERE id = :id"),
            {"id": user_id},
        ).one()
    # Comptes existants : vérifiés d'office, aucune session invalidée ; données conservées
    assert tuple(row) == (True, None)


def _create_legacy_schema(engine) -> None:
    """Schéma créé par create_all avant Alembic : colonnes ajoutées après la révision 0002 absentes."""
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        for table in ("comparisons", "interviews", "cover_letters"):
            conn.execute(text(f"ALTER TABLE {table} DROP COLUMN offer_url"))
        conn.execute(text("ALTER TABLE comparisons DROP COLUMN parent_comparison_id"))


def test_legacy_database_with_saved_cvs_already_created(empty_db):
    """#44 déployée avant Alembic : la table saved_cvs existe déjà, la migration 0002 ne la recrée pas."""
    _create_legacy_schema(empty_db)
    run_migrations(empty_db)
    assert _current(empty_db) == _head()
    assert _schema_diff(empty_db) == []


def test_baseline_is_the_first_revision():
    script = ScriptDirectory.from_config(alembic_config())
    assert script.get_revision(BASELINE_REVISION).down_revision is None
