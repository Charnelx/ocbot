from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    topic_id: int
    title: str
    raw_text_segment: str
    category: Annotated[str, Field(max_length=50)]
    labels: list[Annotated[str, Field(max_length=255)]] = Field(default_factory=list)
    price: Decimal | None = None
    currency: Annotated[str, Field(max_length=3)]
    is_standalone: bool = False


class ItemRead(BaseModel):
    id: int
    topic_id: int
    title: str
    raw_text_segment: str
    category: str
    labels: list[str]
    price: Decimal | None
    currency: str
    is_standalone: bool


class ItemUpdate(BaseModel):
    title: str | None = None
    raw_text_segment: str | None = None
    category: str | None = None
    labels: list[str] | None = None
    price: Decimal | None = None
    currency: str | None = None
    is_standalone: bool | None = None


class SearchResultItem(BaseModel):
    item_id: int
    topic_id: int
    topic_url: str
    title: str
    category: str
    labels: list[str]
    price: Decimal | None
    currency: str
    is_standalone: bool
    raw_text_segment: str
    author: str
    last_update_at: str
    score: float


class SearchResponse(BaseModel):
    total: int
    results: list[SearchResultItem]
