"""Add array_intersection SQL function

Revision ID: 004
Revises: 003_add_item_fts_index
Create Date: 2026-02-24

"""

from collections.abc import Sequence

from alembic import op


revision: str = "004"
down_revision: str | Sequence[str] | None = "003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION array_intersection(a VARCHAR[], b VARCHAR[])
        RETURNS VARCHAR[] AS $$
            SELECT ARRAY(
                SELECT unnest(a)
                INTERSECT
                SELECT unnest(b)
            );
        $$ LANGUAGE sql IMMUTABLE
        """
    )


def downgrade() -> None:
    op.execute("DROP FUNCTION IF EXISTS array_intersection(VARCHAR[], VARCHAR[])")
