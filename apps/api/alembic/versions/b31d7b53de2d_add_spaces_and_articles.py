"""add_spaces_and_articles

Revision ID: b31d7b53de2d
Revises: 20250928_000002
Create Date: 2025-09-28

"""
from typing import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "b31d7b53de2d"
down_revision: str | None = '20250928_000002'
branch_labels: str | Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    # Create articles table
    op.create_table(
        'articles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=300), nullable=False),
        sa.Column('summary', sa.String(length=500), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('author_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('view_count', sa.Integer(), nullable=False, default=0),
        sa.Column('like_count', sa.Integer(), nullable=False, default=0),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_index(op.f('ix_articles_slug'), 'articles', ['slug'], unique=True)

    # Create spaces table
    op.create_table(
        'spaces',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=120), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column('visibility', sa.String(length=20), nullable=False),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('member_count', sa.Integer(), nullable=False, default=1),
        sa.Column('article_count', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("visibility IN ('public', 'private')", name='check_visibility'),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_index(op.f('ix_spaces_slug'), 'spaces', ['slug'], unique=True)
    op.create_index('idx_spaces_visibility_created', 'spaces', ['visibility', 'created_at'], unique=False)
    op.create_index('idx_spaces_tags', 'spaces', ['tags'], unique=False, postgresql_using='gin')

    # Create space_members association table
    op.create_table(
        'space_members',
        sa.Column('space_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False, default='member'),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.CheckConstraint("role IN ('owner', 'moderator', 'member')", name='check_member_role'),
        sa.ForeignKeyConstraint(['space_id'], ['spaces.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('space_id', 'user_id')
    )
    op.create_index('idx_space_members_user', 'space_members', ['user_id'], unique=False)

    # Create space_articles table
    op.create_table(
        'space_articles',
        sa.Column('space_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('article_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('added_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('pinned', sa.Boolean(), nullable=False, default=False),
        sa.Column('added_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['added_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ),
        sa.ForeignKeyConstraint(['space_id'], ['spaces.id'], ),
        sa.PrimaryKeyConstraint('space_id', 'article_id')
    )
    op.create_index('idx_space_articles_added', 'space_articles', ['space_id', 'added_at'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index('idx_space_articles_added', table_name='space_articles')
    op.drop_table('space_articles')

    op.drop_index('idx_space_members_user', table_name='space_members')
    op.drop_table('space_members')

    op.drop_index('idx_spaces_tags', table_name='spaces', postgresql_using='gin')
    op.drop_index('idx_spaces_visibility_created', table_name='spaces')
    op.drop_index(op.f('ix_spaces_slug'), table_name='spaces')
    op.drop_table('spaces')

    op.drop_index(op.f('ix_articles_slug'), table_name='articles')
    op.drop_table('articles')