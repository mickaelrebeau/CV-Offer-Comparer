"""Schéma initial : tables existantes avant l'adoption d'Alembic.

Une base créée auparavant par `Base.metadata.create_all` est marquée à cette révision
(`alembic stamp 0001`, fait automatiquement par app.migrations) au lieu de la rejouer.

Revision ID: 0001
Revises:
Create Date: 2026-10-06

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('users',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('email', sa.String(length=320), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=True),
    sa.Column('google_id', sa.String(length=255), nullable=True),
    sa.Column('full_name', sa.String(length=255), nullable=True),
    sa.Column('avatar_url', sa.String(length=512), nullable=True),
    sa.Column('email_verified_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('password_changed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('google_id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_table('auth_tokens',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('purpose', sa.String(length=32), nullable=False),
    sa.Column('token_hash', sa.String(length=64), nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_auth_tokens_token_hash'), 'auth_tokens', ['token_hash'], unique=True)
    op.create_index(op.f('ix_auth_tokens_user_id'), 'auth_tokens', ['user_id'], unique=False)
    op.create_table('comparisons',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('offer_excerpt', sa.String(length=320), nullable=False),
    sa.Column('cv_excerpt', sa.String(length=320), nullable=False),
    sa.Column('match_percentage', sa.Float(), nullable=False),
    sa.Column('total_items', sa.Integer(), nullable=False),
    sa.Column('matches', sa.Integer(), nullable=False),
    sa.Column('missing', sa.Integer(), nullable=False),
    sa.Column('unclear', sa.Integer(), nullable=False),
    sa.Column('summary', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('items', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('offer_text', sa.Text(), nullable=False),
    sa.Column('cv_text', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_comparisons_user_id'), 'comparisons', ['user_id'], unique=False)
    op.create_table('cover_letters',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('subject', sa.String(length=320), nullable=False),
    sa.Column('job_excerpt', sa.String(length=320), nullable=False),
    sa.Column('cv_excerpt', sa.String(length=320), nullable=False),
    sa.Column('tone', sa.String(length=32), nullable=False),
    sa.Column('length', sa.String(length=32), nullable=False),
    sa.Column('language', sa.String(length=8), nullable=False),
    sa.Column('word_count', sa.Integer(), nullable=False),
    sa.Column('letter', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('cv_text', sa.Text(), nullable=False),
    sa.Column('job_text', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cover_letters_user_id'), 'cover_letters', ['user_id'], unique=False)
    op.create_table('interviews',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('job_excerpt', sa.String(length=320), nullable=False),
    sa.Column('cv_excerpt', sa.String(length=320), nullable=False),
    sa.Column('score_global', sa.Float(), nullable=False),
    sa.Column('num_questions', sa.Integer(), nullable=False),
    sa.Column('duration_seconds', sa.Integer(), nullable=False),
    sa.Column('questions', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('answers', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('analysis', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('cv_text', sa.Text(), nullable=False),
    sa.Column('job_text', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_interviews_user_id'), 'interviews', ['user_id'], unique=False)
    op.create_table('user_llm_credentials',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('provider', sa.String(length=32), nullable=False),
    sa.Column('encrypted_api_key', sa.Text(), nullable=False),
    sa.Column('key_hint', sa.String(length=32), nullable=False),
    sa.Column('model', sa.String(length=128), nullable=False),
    sa.Column('base_url', sa.String(length=300), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'provider', name='uq_user_llm_credentials_user_provider')
    )
    op.create_index(op.f('ix_user_llm_credentials_user_id'), 'user_llm_credentials', ['user_id'], unique=False)
    op.create_index('uq_user_llm_credentials_active', 'user_llm_credentials', ['user_id'], unique=True, postgresql_where=sa.text('is_active'))


def downgrade() -> None:
    op.drop_index('uq_user_llm_credentials_active', table_name='user_llm_credentials', postgresql_where=sa.text('is_active'))
    op.drop_index(op.f('ix_user_llm_credentials_user_id'), table_name='user_llm_credentials')
    op.drop_table('user_llm_credentials')
    op.drop_index(op.f('ix_interviews_user_id'), table_name='interviews')
    op.drop_table('interviews')
    op.drop_index(op.f('ix_cover_letters_user_id'), table_name='cover_letters')
    op.drop_table('cover_letters')
    op.drop_index(op.f('ix_comparisons_user_id'), table_name='comparisons')
    op.drop_table('comparisons')
    op.drop_index(op.f('ix_auth_tokens_user_id'), table_name='auth_tokens')
    op.drop_index(op.f('ix_auth_tokens_token_hash'), table_name='auth_tokens')
    op.drop_table('auth_tokens')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
