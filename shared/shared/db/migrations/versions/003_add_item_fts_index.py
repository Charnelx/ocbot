"""Add FTS index on items.raw_text_segment

Revision ID: 003
Revises: 002_add_enrichment_tracking
Create Date: 2026-02-24

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "003"
down_revision: str | Sequence[str] | None = "002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_item_fts "
        "ON items USING GIN (to_tsvector('english', raw_text_segment))"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_item_fts")
