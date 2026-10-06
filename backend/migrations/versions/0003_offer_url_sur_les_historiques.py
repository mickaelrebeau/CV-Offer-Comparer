"""Lien de l'annonce (offer_url) sur les historiques : comparaisons, entretiens, lettres.

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-06

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0003'
down_revision: Union[str, Sequence[str], None] = '0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLES = ('comparisons', 'interviews', 'cover_letters')


def upgrade() -> None:
    for table in TABLES:
        op.add_column(table, sa.Column('offer_url', sa.String(length=2048), nullable=True))


def downgrade() -> None:
    for table in TABLES:
        op.drop_column(table, 'offer_url')
