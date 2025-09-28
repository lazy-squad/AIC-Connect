"""extend user profile fields"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from aic_hub.usernames import normalize_username, USERNAME_MAX_LENGTH, USERNAME_MIN_LENGTH

revision: str = "20250928_000003"
down_revision: str | None = "20250928_000002"
branch_labels: str | Sequence[str] | None = None
depends_on: Sequence[str] | None = None


users_table = sa.table(
  "users",
  sa.column("id", postgresql.UUID(as_uuid=True)),
  sa.column("email", sa.String(length=255)),
  sa.column("username", sa.String(length=32)),
  sa.column("created_at", sa.DateTime(timezone=True)),
)


def _apply_suffix(base: str, suffix: int) -> str:
  suffix_str = f"-{suffix}"
  allowed_length = USERNAME_MAX_LENGTH - len(suffix_str)
  trimmed = base[:allowed_length].rstrip("-") or base[:allowed_length]
  candidate = f"{trimmed}{suffix_str}"
  if len(candidate) < USERNAME_MIN_LENGTH:
    candidate = (candidate + ("x" * USERNAME_MIN_LENGTH))[:USERNAME_MIN_LENGTH]
  return candidate


def _generate_unique(base: str, taken: set[str]) -> str:
  root = normalize_username(base)
  candidate = root
  suffix = 1
  while candidate in taken:
    candidate = _apply_suffix(root, suffix)
    suffix += 1
  taken.add(candidate)
  return candidate


def _backfill_usernames() -> None:
  bind = op.get_bind()
  existing_usernames = {
    row.username
    for row in bind.execute(sa.select(users_table.c.username).where(users_table.c.username.is_not(None)))
    if row.username
  }

  rows = bind.execute(
    sa.select(users_table.c.id, users_table.c.email, users_table.c.username).order_by(users_table.c.created_at)
  ).all()
  for row in rows:
    if row.email is None:
      continue
    username = row.username
    if username:
      if username not in existing_usernames:
        existing_usernames.add(username)
      continue
    local_part = row.email.split("@", 1)[0]
    generated = _generate_unique(local_part, existing_usernames)
    bind.execute(
      users_table.update().where(users_table.c.id == row.id).values(username=generated)
    )


def upgrade() -> None:
  op.add_column("users", sa.Column("username", sa.String(length=32), nullable=True))
  op.add_column("users", sa.Column("github_username", sa.Text(), nullable=True))
  op.add_column("users", sa.Column("avatar_url", sa.Text(), nullable=True))
  op.add_column("users", sa.Column("bio", sa.Text(), nullable=True))
  op.add_column("users", sa.Column("company", sa.Text(), nullable=True))
  op.add_column("users", sa.Column("location", sa.Text(), nullable=True))
  op.add_column(
    "users",
    sa.Column(
      "expertise_tags",
      postgresql.ARRAY(sa.Text()),
      server_default=sa.text("'{}'"),
      nullable=False,
    ),
  )
  op.add_column("users", sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True))

  _backfill_usernames()

  op.alter_column("users", "username", nullable=False)
  op.create_unique_constraint("uq_users_username", "users", ["username"])


def downgrade() -> None:
  op.drop_constraint("uq_users_username", "users", type_="unique")
  op.drop_column("users", "updated_at")
  op.drop_column("users", "expertise_tags")
  op.drop_column("users", "location")
  op.drop_column("users", "company")
  op.drop_column("users", "bio")
  op.drop_column("users", "avatar_url")
  op.drop_column("users", "github_username")
  op.drop_column("users", "username")
