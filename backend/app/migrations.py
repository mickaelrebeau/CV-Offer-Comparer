"""Application des migrations Alembic au démarrage de l'API.

- Base vide : toutes les migrations sont jouées.
- Base créée avant Alembic (`create_all`, sans table alembic_version) : les anciennes
  migrations ad hoc la mettent au niveau du schéma initial, puis elle est marquée à la
  révision 0001 (`stamp`) avant d'appliquer les suivantes.

Tout se fait dans une seule transaction, sous verrou consultatif PostgreSQL : deux instances
qui démarrent en même temps n'appliquent pas les migrations deux fois.
"""

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, text
from sqlalchemy.engine import Connection, Engine

ALEMBIC_INI = Path(__file__).resolve().parent.parent / "alembic.ini"
BASELINE_REVISION = "0001"
# Identifiant arbitraire du verrou consultatif (pg_advisory_xact_lock)
MIGRATION_LOCK_ID = 7_310_442_001


def alembic_config(connection: Connection | None = None) -> Config:
    config = Config(str(ALEMBIC_INI))
    config.attributes["configure_logger"] = False
    if connection is not None:
        config.attributes["connection"] = connection
    return config


def is_legacy_schema(connection: Connection) -> bool:
    """Tables applicatives présentes mais jamais versionnées par Alembic."""
    tables = inspect(connection)
    return tables.has_table("users") and not tables.has_table("alembic_version")


def upgrade_legacy_schema(connection: Connection) -> None:
    """Migrations ad hoc d'avant Alembic (idempotentes) : schéma amené au niveau de 0001."""
    columns = {column["name"] for column in inspect(connection).get_columns("users")}
    if "email_verified_at" not in columns:
        # Les comptes créés avant la vérification e-mail sont considérés comme vérifiés
        connection.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified_at TIMESTAMPTZ"))
        connection.execute(text("UPDATE users SET email_verified_at = created_at WHERE email_verified_at IS NULL"))
    if "password_changed_at" not in columns:
        # Vide pour les comptes existants : aucune session invalidée
        connection.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS password_changed_at TIMESTAMPTZ"))


def run_migrations(engine: Engine, revision: str = "head") -> None:
    with engine.begin() as connection:
        connection.execute(text("SELECT pg_advisory_xact_lock(:id)"), {"id": MIGRATION_LOCK_ID})
        config = alembic_config(connection)
        if is_legacy_schema(connection):
            print("[DB] Base créée avant Alembic : mise à niveau puis marquage à la révision initiale")
            upgrade_legacy_schema(connection)
            command.stamp(config, BASELINE_REVISION)
        command.upgrade(config, revision)
