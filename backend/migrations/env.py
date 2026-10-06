"""Environnement Alembic : base de l'app (DATABASE_URL) et métadonnées des modèles ORM."""

from logging.config import fileConfig

from alembic import context
from sqlalchemy.engine import Connection

from app.models import tables  # noqa: F401  (enregistre toutes les tables)
from app.db import Base, engine

config = context.config

# En ligne de commande uniquement : au démarrage de l'API, la config de logs d'uvicorn est conservée
if config.config_file_name and config.attributes.get("configure_logger", True):
    fileConfig(config.config_file_name, disable_existing_loggers=False)

target_metadata = Base.metadata


def _configure(**kwargs) -> None:
    context.configure(target_metadata=target_metadata, compare_type=True, **kwargs)


def run_migrations_offline() -> None:
    """`alembic upgrade --sql` : génère le SQL sans se connecter."""
    _configure(url=engine.url.render_as_string(hide_password=False), literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def _run_with(connection: Connection) -> None:
    _configure(connection=connection)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    # Connexion fournie par app.migrations (verrou + transaction déjà ouverts)
    connection = config.attributes.get("connection")
    if connection is not None:
        _run_with(connection)
        return
    with engine.connect() as connection:
        _run_with(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
