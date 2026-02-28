"""Add created_at column to topics table

Revision ID: 007
Revises: 006
Create Date: 2026-02-27

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "007"
down_revision: str | Sequence[str] | None = "006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "topics",
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index("idx_topics_created_at", "topics", ["created_at"])


def downgrade() -> None:
    op.drop_index("idx_topics_created_at", table_name="topics")
    op.drop_column("topics", "created_at")
