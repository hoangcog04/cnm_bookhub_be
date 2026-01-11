"""add cart.

Revision ID: aef89969b1e5
Revises: 967c28cee86b
Create Date: 2026-01-07 03:13:06.936465

"""
from alembic import op
import sqlalchemy as sa
from fastapi_users_db_sqlalchemy.generics import GUID


# revision identifiers, used by Alembic.
revision = 'aef89969b1e5'
down_revision = '967c28cee86b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "cart",
        sa.Column("user_id", GUID(), nullable=False),
        sa.Column("book_id", sa.Uuid(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"]),
        sa.PrimaryKeyConstraint("user_id", "book_id"),
    )

def downgrade() -> None:
    op.drop_table("cart")

