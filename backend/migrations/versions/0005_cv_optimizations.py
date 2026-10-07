"""Optimiseur de CV : historique cv_optimizations.

Revision ID: 0005
Revises: 0004
Create Date: 2026-10-07

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0005'
down_revision: Union[str, Sequence[str], None] = '0004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('cv_optimizations',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('comparison_id', sa.UUID(), nullable=True),
    sa.Column('job_excerpt', sa.String(length=320), nullable=False),
    sa.Column('cv_excerpt', sa.String(length=320), nullable=False),
    sa.Column('summary', sa.Text(), nullable=False),
    sa.Column('suggestion_count', sa.Integer(), nullable=False),
    sa.Column('suggestions', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('cv_text', sa.Text(), nullable=False),
    sa.Column('job_text', sa.Text(), nullable=False),
    sa.Column('offer_url', sa.String(length=2048), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['comparison_id'], ['comparisons.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cv_optimizations_comparison_id'), 'cv_optimizations', ['comparison_id'], unique=False)
    op.create_index(op.f('ix_cv_optimizations_user_id'), 'cv_optimizations', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_cv_optimizations_user_id'), table_name='cv_optimizations')
    op.drop_index(op.f('ix_cv_optimizations_comparison_id'), table_name='cv_optimizations')
    op.drop_table('cv_optimizations')
