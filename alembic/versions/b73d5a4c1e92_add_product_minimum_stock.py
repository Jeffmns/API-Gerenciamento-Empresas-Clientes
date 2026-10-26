"""Add minimum stock to products.

Revision ID: b73d5a4c1e92
Revises: a1272293788f
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b73d5a4c1e92"
down_revision: Union[str, Sequence[str], None] = "a1272293788f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "produtos",
        sa.Column(
            "estoque_minimo",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("produtos", "estoque_minimo")
