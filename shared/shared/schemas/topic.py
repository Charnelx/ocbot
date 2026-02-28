from datetime import datetime
from typing import Annotated

from pydantic import Field


class TopicBase:
    pass


class TopicCreate(TopicBase):
    external_id: Annotated[str, Field(max_length=255)]
    title: str
    raw_content: str
    clean_content: str
    content_hash: Annotated[str, Field(max_length=64)]
    author: Annotated[str, Field(max_length=255)]
    last_update_at: datetime


class TopicRead(TopicBase):
    id: int
    external_id: str
    title: str
    raw_content: str
    clean_content: str
    content_hash: str
    author: str
    last_update_at: datetime
    scraped_at: datetime
    enriched: bool


class TopicUpdate(TopicBase):
    title: str | None = None
    raw_content: str | None = None
    clean_content: str | None = None
    content_hash: str | None = None
    author: str | None = None
    last_update_at: datetime | None = None
    scraped_at: datetime | None = None
    enriched: bool | None = None
