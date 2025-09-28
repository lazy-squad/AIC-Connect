"""create auth tables"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20250928_000002"
down_revision: str | None = "20240928_000001"
branch_labels: str | Sequence[str] | None = None
depends_on: Sequence[str] | None = None

oauth_provider_enum = sa.Enum("github", name="oauth_provider")
auth_action_enum = sa.Enum("signup", "login", name="auth_action")


def upgrade() -> None:
  bind = op.get_bind()
  oauth_provider_enum.create(bind, checkfirst=True)
  auth_action_enum.create(bind, checkfirst=True)

  op.create_table(
    "users",
    sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
    sa.Column("email", sa.String(length=255), nullable=False, unique=True),
    sa.Column("password_hash", sa.String(length=512), nullable=True),
    sa.Column("display_name", sa.String(length=255), nullable=True),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
  )

  op.create_table(
    "oauth_accounts",
    sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
    sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    sa.Column("provider", oauth_provider_enum, nullable=False),
    sa.Column("provider_account_id", sa.String(length=255), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    sa.UniqueConstraint("provider", "provider_account_id", name="uq_oauth_provider_account"),
  )

  op.create_table(
    "auth_attempts",
    sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
    sa.Column("action", auth_action_enum, nullable=False),
    sa.Column("email_hash", sa.String(length=128), nullable=True),
    sa.Column("ip_address", sa.String(length=64), nullable=True),
    sa.Column("success", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    sa.Column("reason", sa.String(length=64), nullable=True),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
  )
  op.create_index("ix_auth_attempts_email_hash", "auth_attempts", ["email_hash"])
  op.create_index("ix_auth_attempts_ip_address", "auth_attempts", ["ip_address"])
  op.create_index("ix_auth_attempts_created_at", "auth_attempts", ["created_at"])


def downgrade() -> None:
  op.drop_index("ix_auth_attempts_created_at", table_name="auth_attempts")
  op.drop_index("ix_auth_attempts_ip_address", table_name="auth_attempts")
  op.drop_index("ix_auth_attempts_email_hash", table_name="auth_attempts")
  op.drop_table("auth_attempts")

  op.drop_table("oauth_accounts")

  op.drop_table("users")

  bind = op.get_bind()
  auth_action_enum.drop(bind, checkfirst=True)
  oauth_provider_enum.drop(bind, checkfirst=True)
