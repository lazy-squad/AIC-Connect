"""Add profile fields and expertise tags to User"""

from typing import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "f010abb74553"
down_revision: str | None = 'a760eef026b5'
branch_labels: str | Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    # Add new profile fields to users table
    op.add_column('users', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('username', sa.String(length=50), nullable=True))
    op.add_column('users', sa.Column('github_username', sa.String(length=50), nullable=True))
    op.add_column('users', sa.Column('avatar_url', sa.String(length=500), nullable=True))
    op.add_column('users', sa.Column('bio', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('company', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('location', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('expertise_tags', postgresql.ARRAY(sa.String()), server_default='{}', nullable=False))

    # Create indexes
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    op.create_index('idx_user_expertise_tags', 'users', ['expertise_tags'], postgresql_using='gin')


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_user_expertise_tags', table_name='users')
    op.drop_index('ix_users_username', table_name='users')

    # Drop columns
    op.drop_column('users', 'expertise_tags')
    op.drop_column('users', 'location')
    op.drop_column('users', 'company')
    op.drop_column('users', 'bio')
    op.drop_column('users', 'avatar_url')
    op.drop_column('users', 'github_username')
    op.drop_column('users', 'username')
    op.drop_column('users', 'updated_at')
