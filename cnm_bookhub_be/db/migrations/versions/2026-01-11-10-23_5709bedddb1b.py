"""merge heads.

Revision ID: 5709bedddb1b
Revises: aef89969b1e5, d8a476a3312f, c245b7ef033b
Create Date: 2026-01-11 10:23:40.324288

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5709bedddb1b'
down_revision = ('aef89969b1e5', 'd8a476a3312f', 'c245b7ef033b')
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Run the migration."""
    


def downgrade() -> None:
    """Undo the migration."""
    
