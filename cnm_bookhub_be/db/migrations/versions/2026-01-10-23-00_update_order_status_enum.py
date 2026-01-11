"""Update OrderStatus enum with all values.

Revision ID: update_order_status_enum
Revises: 07cc3d04168a
Create Date: 2026-01-10 23:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "update_order_status_enum"
down_revision = "07cc3d04168a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Run the migration."""
    # Alter the status column to use the proper enum type with MySQL syntax
    op.execute(
        "ALTER TABLE orders MODIFY COLUMN status ENUM('pending', 'require_payment', 'cancelled', 'charged', 'shipped', 'completed') NOT NULL"
    )


def downgrade() -> None:
    """Undo the migration."""
    # Revert back to VARCHAR
    op.execute("ALTER TABLE orders MODIFY COLUMN status VARCHAR(50) NOT NULL")
