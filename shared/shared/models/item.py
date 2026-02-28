from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ARRAY, Boolean, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from shared.db.connection import Base

if TYPE_CHECKING:
    from shared.models.topic import Topic


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    topic_id: Mapped[int] = mapped_column(
        ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    raw_text_segment: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    labels: Mapped[list[str]] = mapped_column(
        ARRAY(String(255)),
        nullable=False,
        default="{}",
    )
    price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1024), nullable=True)
    is_standalone: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    topic: Mapped["Topic"] = relationship("Topic", back_populates="items")
