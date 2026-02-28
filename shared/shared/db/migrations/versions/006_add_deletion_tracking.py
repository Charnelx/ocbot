"""Add deletion tracking columns to topics table

Revision ID: 006
Revises: 005
Create Date: 2026-02-26

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "006"
down_revision: str | Sequence[str] | None = "005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "topics",
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "topics",
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.add_column(
        "topics",
        sa.Column("is_closed", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "topics",
        sa.Column("closed_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )

    op.create_index("idx_topics_is_deleted", "topics", ["is_deleted"])
    op.create_index("idx_topics_is_closed", "topics", ["is_closed"])
    op.create_index("idx_topics_last_update_at", "topics", ["last_update_at"])


def downgrade() -> None:
    op.drop_index("idx_topics_last_update_at", table_name="topics")
    op.drop_index("idx_topics_is_closed", table_name="topics")
    op.drop_index("idx_topics_is_deleted", table_name="topics")
    op.drop_column("topics", "closed_at")
    op.drop_column("topics", "is_closed")
    op.drop_column("topics", "deleted_at")
    op.drop_column("topics", "is_deleted")
