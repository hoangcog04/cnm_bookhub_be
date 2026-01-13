"""merge fixed_shipped_enum and add_category_description.

Revision ID: 052ed3a43d28
Revises: add_category_description, fix_shipped_enum
Create Date: 2026-01-12 13:18:25.161402

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '052ed3a43d28'
down_revision = ('add_category_description', 'fix_shipped_enum')
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Run the migration."""
    


def downgrade() -> None:
    """Undo the migration."""
    
