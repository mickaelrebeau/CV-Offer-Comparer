"""Suivi de candidatures : table applications et rattachement des analyses, entretiens et lettres.

Revision ID: 0006
Revises: 0005
Create Date: 2026-10-07

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0006'
down_revision: Union[str, Sequence[str], None] = '0005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

LINKED_TABLES = ('comparisons', 'interviews', 'cover_letters')


def upgrade() -> None:
    op.create_table('applications',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('company', sa.String(length=200), nullable=False),
    sa.Column('offer_url', sa.String(length=2048), nullable=True),
    sa.Column('offer_text', sa.Text(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('notes', sa.Text(), nullable=False),
    sa.Column('applied_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_applications_user_id'), 'applications', ['user_id'], unique=False)
    for table in LINKED_TABLES:
        op.add_column(table, sa.Column('application_id', sa.UUID(), nullable=True))
        op.create_index(op.f(f'ix_{table}_application_id'), table, ['application_id'], unique=False)
        op.create_foreign_key(
            f'{table}_application_id_fkey', table, 'applications', ['application_id'], ['id'], ondelete='SET NULL'
        )


def downgrade() -> None:
    for table in LINKED_TABLES:
        op.drop_constraint(f'{table}_application_id_fkey', table, type_='foreignkey')
        op.drop_index(op.f(f'ix_{table}_application_id'), table_name=table)
        op.drop_column(table, 'application_id')
    op.drop_index(op.f('ix_applications_user_id'), table_name='applications')
    op.drop_table('applications')
