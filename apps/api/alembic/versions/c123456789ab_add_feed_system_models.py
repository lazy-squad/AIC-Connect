"""add feed system models

Revision ID: c123456789ab
Revises: b31d7b53de2d
Create Date: 2025-09-28

"""
from typing import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "c123456789ab"
down_revision: str | None = 'b31d7b53de2d'
branch_labels: str | Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    # Create user_preferences table
    op.create_table(
        'user_preferences',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('preferred_tags', postgresql.ARRAY(sa.String()), nullable=False, server_default='{}'),
        sa.Column('feed_view', sa.String(length=20), nullable=False, server_default='latest'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('user_id')
    )

    # Create activities table
    op.create_table(
        'activities',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('gen_random_uuid()')),
        sa.Column('actor_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('target_type', sa.String(length=50), nullable=False),
        sa.Column('target_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('activity_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['actor_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for activities table
    op.create_index('idx_activities_created_at', 'activities', ['created_at'], unique=False)
    op.create_index('idx_activities_actor_created', 'activities', ['actor_id', 'created_at'], unique=False)
    op.create_index('idx_activities_target', 'activities', ['target_type', 'target_id'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_activities_target', table_name='activities')
    op.drop_index('idx_activities_actor_created', table_name='activities')
    op.drop_index('idx_activities_created_at', table_name='activities')

    # Drop tables
    op.drop_table('activities')
    op.drop_table('user_preferences')