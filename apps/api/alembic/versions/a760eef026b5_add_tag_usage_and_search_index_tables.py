"""Add tag usage and search index tables

Revision ID: a760eef026b5
Revises: c123456789ab
Create Date: 2025-09-28

"""
from typing import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "a760eef026b5"
down_revision: str | None = 'c123456789ab'
branch_labels: str | Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    # Create tag_usage table
    op.create_table('tag_usage',
        sa.Column('tag', sa.String(50), nullable=False),
        sa.Column('article_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('space_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('user_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('trending_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('week_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('month_count', sa.Integer(), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('tag')
    )

    # Create indexes for tag_usage
    op.create_index('idx_tag_usage_trending', 'tag_usage', ['trending_score'])
    op.create_index('idx_tag_usage_counts', 'tag_usage', ['article_count', 'space_count', 'user_count'])

    # Create search_index table
    op.create_table('search_index',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('entity_type', sa.String(20), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(300), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column('search_vector', postgresql.TSVECTOR(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for search_index
    op.create_index('idx_search_entity', 'search_index', ['entity_type', 'entity_id'])
    op.create_index('idx_search_tags', 'search_index', ['tags'], postgresql_using='gin')
    op.create_index('idx_search_vector', 'search_index', ['search_vector'], postgresql_using='gin')

    # Create PostgreSQL text search configuration
    op.execute("CREATE TEXT SEARCH CONFIGURATION IF NOT EXISTS english_stem (COPY = english);")

    # Create search indexes for existing tables
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_articles_search
        ON articles
        USING gin(to_tsvector('english', title || ' ' || COALESCE(summary, '') || ' ' || array_to_string(tags, ' ')))
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_spaces_search
        ON spaces
        USING gin(to_tsvector('english', name || ' ' || COALESCE(description, '') || ' ' || array_to_string(tags, ' ')))
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_users_search
        ON users
        USING gin(to_tsvector('english', COALESCE(display_name, '') || ' ' || email))
    """)


def downgrade() -> None:
    # Drop search indexes on existing tables
    op.execute("DROP INDEX IF EXISTS idx_users_search")
    op.execute("DROP INDEX IF EXISTS idx_spaces_search")
    op.execute("DROP INDEX IF EXISTS idx_articles_search")

    # Drop indexes for search_index
    op.drop_index('idx_search_vector', table_name='search_index')
    op.drop_index('idx_search_tags', table_name='search_index')
    op.drop_index('idx_search_entity', table_name='search_index')

    # Drop search_index table
    op.drop_table('search_index')

    # Drop indexes for tag_usage
    op.drop_index('idx_tag_usage_counts', table_name='tag_usage')
    op.drop_index('idx_tag_usage_trending', table_name='tag_usage')

    # Drop tag_usage table
    op.drop_table('tag_usage')
