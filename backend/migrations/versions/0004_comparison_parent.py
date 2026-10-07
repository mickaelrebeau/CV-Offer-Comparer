"""Réanalyse d'une offre avec un CV mis à jour : comparaison parente (fil de versions).

Revision ID: 0004
Revises: 0003
Create Date: 2026-10-07

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0004'
down_revision: Union[str, Sequence[str], None] = '0003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('comparisons', sa.Column('parent_comparison_id', sa.UUID(), nullable=True))
    op.create_index(op.f('ix_comparisons_parent_comparison_id'), 'comparisons', ['parent_comparison_id'], unique=False)
    op.create_foreign_key(
        'comparisons_parent_comparison_id_fkey',
        'comparisons',
        'comparisons',
        ['parent_comparison_id'],
        ['id'],
        ondelete='SET NULL',
    )


def downgrade() -> None:
    op.drop_constraint('comparisons_parent_comparison_id_fkey', 'comparisons', type_='foreignkey')
    op.drop_index(op.f('ix_comparisons_parent_comparison_id'), table_name='comparisons')
    op.drop_column('comparisons', 'parent_comparison_id')
