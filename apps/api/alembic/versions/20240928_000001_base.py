"""empty base revision"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20240928_000001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
  pass


def downgrade() -> None:
  pass
