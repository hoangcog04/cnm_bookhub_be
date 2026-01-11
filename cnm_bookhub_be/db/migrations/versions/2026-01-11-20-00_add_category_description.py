"""Add description field to categories table.

Revision ID: add_category_description
Revises: 8bf2bfdf5704
Create Date: 2026-01-11 20:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "add_category_description"
down_revision = "8bf2bfdf5704"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add description column to categories table."""
    # Check if column already exists before adding
    op.add_column(
        "categories",
        sa.Column("description", sa.String(length=500), nullable=True),
    )


def downgrade() -> None:
    """Remove description column from categories table."""
    op.drop_column("categories", "description")
