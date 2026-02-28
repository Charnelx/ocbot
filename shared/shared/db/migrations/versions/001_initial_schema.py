"""Initial schema with topics, items, and vector indexes

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-02-21

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = "001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "topics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("external_id", sa.String(255), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("raw_content", sa.Text(), nullable=False),
        sa.Column("clean_content", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("author", sa.String(255), nullable=False),
        sa.Column(
            "last_update_at", postgresql.TIMESTAMP(timezone=True), nullable=False
        ),
        sa.Column("scraped_at", postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("enriched", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("embedding", Vector(1024), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_topics_external_id", "topics", ["external_id"], unique=True)
    op.create_index("idx_topics_content_hash", "topics", ["content_hash"])
    op.create_index("idx_topics_enriched", "topics", ["enriched"])

    op.create_table(
        "items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("topic_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("raw_text_segment", sa.Text(), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column(
            "labels",
            postgresql.ARRAY(sa.String(255)),
            nullable=False,
            server_default="{}",
        ),
        sa.Column("price", sa.Numeric(12, 2), nullable=True),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("embedding", Vector(1024), nullable=True),
        sa.Column(
            "is_standalone", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.ForeignKeyConstraint(["topic_id"], ["topics.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_items_topic_id", "items", ["topic_id"])
    op.create_index("idx_items_category", "items", ["category"])
    op.create_index("idx_items_labels", "items", ["labels"], postgresql_using="gin")

    op.execute("""
        CREATE INDEX idx_topics_embedding_hnsw ON topics 
        USING hnsw (embedding vector_cosine_ops) 
        WITH (m=16, ef_construction=64)
    """)
    op.execute("""
        CREATE INDEX idx_items_embedding_hnsw ON items 
        USING hnsw (embedding vector_cosine_ops) 
        WITH (m=16, ef_construction=64)
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_items_embedding_hnsw")
    op.execute("DROP INDEX IF EXISTS idx_topics_embedding_hnsw")
    op.drop_table("items")
    op.drop_table("topics")
    op.execute("DROP EXTENSION IF EXISTS vector")
