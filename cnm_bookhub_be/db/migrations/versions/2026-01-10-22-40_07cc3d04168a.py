"""merge cart and payment changes.

Revision ID: 07cc3d04168a
Revises: aef89969b1e5, c245b7ef033b
Create Date: 2026-01-10 22:40:05.353228

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "07cc3d04168a"
down_revision = ("aef89969b1e5", "c245b7ef033b")
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Run the migration."""


def downgrade() -> None:
    """Undo the migration."""
