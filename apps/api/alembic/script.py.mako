"""${message}"""

from typing import Sequence

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

revision: str = "${up_revision}"
down_revision: str | None = ${repr(down_revision)}
branch_labels: str | Sequence[str] | None = ${repr(branch_labels)}
depends_on: Sequence[str] | None = ${repr(depends_on)}


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
