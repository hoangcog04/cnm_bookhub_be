"""merge heads.

Revision ID: 8bf2bfdf5704
Revises: 02c9e6a0570e, 93e02957c1d2
Create Date: 2026-01-11 18:34:54.308899

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8bf2bfdf5704"
down_revision = ("02c9e6a0570e", "93e02957c1d2")
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Run the migration."""


def downgrade() -> None:
    """Undo the migration."""
