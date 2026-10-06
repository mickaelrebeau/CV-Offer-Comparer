"""Bibliothèque de CV enregistrés (saved_cvs).

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-06

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0002'
down_revision: Union[str, Sequence[str], None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Table déjà créée par create_all si #44 a été déployée avant Alembic
    if sa.inspect(op.get_bind()).has_table('saved_cvs'):
        return
    op.create_table('saved_cvs',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('label', sa.String(length=80), nullable=False),
    sa.Column('text', sa.Text(), nullable=False),
    sa.Column('source_filename', sa.String(length=255), nullable=True),
    sa.Column('is_default', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_saved_cvs_user_id'), 'saved_cvs', ['user_id'], unique=False)
    op.create_index('uq_saved_cvs_default', 'saved_cvs', ['user_id'], unique=True, postgresql_where=sa.text('is_default'))


def downgrade() -> None:
    op.drop_index('uq_saved_cvs_default', table_name='saved_cvs', postgresql_where=sa.text('is_default'))
    op.drop_index(op.f('ix_saved_cvs_user_id'), table_name='saved_cvs')
    op.drop_table('saved_cvs')
