"""Fix shipped enum values to delivery_in_progress.

Revision ID: fix_shipped_enum
Revises: 8bf2bfdf5704
Create Date: 2026-01-12 00:00:00.000000

"""

from alembic import op
from sqlalchemy import VARCHAR


# revision identifiers, used by Alembic.
revision = "fix_shipped_enum"
down_revision = "8bf2bfdf5704"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Run the migration."""
    # First, convert the ENUM column to VARCHAR to allow any value
    op.alter_column(
        'orders',
        'status',
        type_=VARCHAR(50),
        existing_type=None,
        nullable=False
    )
    
    # Now update the old values to the new ones
    op.execute("UPDATE orders SET status = 'delivery_in_progress' WHERE status = 'shipped'")
    op.execute("UPDATE orders SET status = 'require_payment' WHERE status = 'pending'")
    op.execute("UPDATE orders SET status = 'cancelled' WHERE status = 'charged'")


def downgrade() -> None:
    """Undo the migration."""
    pass
