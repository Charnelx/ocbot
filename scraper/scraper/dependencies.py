from collections.abc import AsyncGenerator
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from shared.db.connection import async_session_factory

from scraper.config import scraper_settings
from scraper.ingestion.embedder import TopicEmbedder
from scraper.repository import TopicRepository
from scraper.scraper.client import ForumClient


def create_forum_client(
    bulk_size: int | None = None,
    user_agent: str | None = None,
) -> ForumClient:
    """Factory function for ForumClient with proper lifecycle management."""
    return ForumClient(
        base_url=scraper_settings.forum_base_url,
        user_agent=user_agent or scraper_settings.default_user_agent,
        bulk_size=bulk_size or scraper_settings.default_bulk_size,
        topics_per_page=scraper_settings.topics_per_page,
    )


@lru_cache
def get_topic_embedder() -> TopicEmbedder:
    """Cached embedder instance - expensive to create."""
    return TopicEmbedder(model_name=scraper_settings.embedding_model)


async def get_db_repository() -> AsyncGenerator[TopicRepository]:
    """Dependency that yields a repository with proper session cleanup."""
    async with async_session_factory() as session:
        yield TopicRepository(session)


ForumClientDep = Annotated[ForumClient, Depends(create_forum_client)]
TopicEmbedderDep = Annotated[TopicEmbedder, Depends(get_topic_embedder)]
TopicRepositoryDep = Annotated[TopicRepository, Depends(get_db_repository)]
