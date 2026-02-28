"""Add search_stats and label_stats tables for precision ranking

Revision ID: 005
Revises: 004
Create Date: 2026-02-25

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "005"
down_revision: str | Sequence[str] | None = "004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "label_stats",
        sa.Column("label", sa.Text(), nullable=False),
        sa.Column("df", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("label"),
    )
    op.create_index("idx_label_stats_df", "label_stats", ["df"])

    op.execute("""
        CREATE TABLE search_stats (
            id INTEGER PRIMARY KEY DEFAULT 1,
            total_items INTEGER NOT NULL,
            avg_label_count FLOAT NOT NULL,
            max_idf FLOAT NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)

    op.execute("""
        INSERT INTO search_stats (id, total_items, avg_label_count, max_idf)
        VALUES (1, 0, 0.0, 1.0)
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS search_stats")
    op.drop_index("idx_label_stats_df", table_name="label_stats")
    op.drop_table("label_stats")
