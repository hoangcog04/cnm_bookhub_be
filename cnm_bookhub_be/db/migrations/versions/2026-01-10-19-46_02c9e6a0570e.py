"""merge heads.

Revision ID: 02c9e6a0570e
Revises: aef89969b1e5, c245b7ef033b
Create Date: 2026-01-10 19:46:06.550732

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "02c9e6a0570e"
down_revision = ("aef89969b1e5", "c245b7ef033b")
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Run the migration."""


def downgrade() -> None:
    """Undo the migration."""
