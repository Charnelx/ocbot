"""Add enrichment tracking columns to topics

Revision ID: 002
Revises: 001_initial_schema
Create Date: 2026-02-23

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "002"
down_revision: str | Sequence[str] | None = "001_initial_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "topics",
        sa.Column(
            "enrichment_attempts", sa.Integer(), nullable=False, server_default="0"
        ),
    )
    op.add_column(
        "topics",
        sa.Column("enrichment_error", sa.Text(), nullable=True),
    )
    op.create_index(
        "idx_topics_enrichment_queue",
        "topics",
        ["enriched", "enrichment_attempts"],
        postgresql_where=sa.text("enriched = false"),
    )


def downgrade() -> None:
    op.drop_index("idx_topics_enrichment_queue", table_name="topics")
    op.drop_column("topics", "enrichment_error")
    op.drop_column("topics", "enrichment_attempts")
