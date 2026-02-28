import logging
from datetime import datetime

from shared.models.topic import Topic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class TopicRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_external_id(self, external_id: str) -> Topic | None:
        result = await self.session.execute(select(Topic).where(Topic.external_id == external_id))
        return result.scalar_one_or_none()

    async def get_content_hash(self, external_id: str) -> str | None:
        result = await self.session.execute(select(Topic.content_hash).where(Topic.external_id == external_id))
        return result.scalar_one_or_none()

    async def upsert_topic(
        self,
        external_id: str,
        title: str,
        raw_content: str,
        clean_content: str,
        content_hash: str,
        author: str,
        last_update_at: datetime,
        embedding: list[float] | None,
        is_closed: bool = False,
        created_at: datetime | None = None,
    ) -> tuple[Topic, bool]:
        existing_topic = await self.get_by_external_id(external_id)

        if existing_topic:
            if existing_topic.content_hash == content_hash:
                logger.debug(
                    "Topic content unchanged, skipping",
                    extra={"external_id": external_id},
                )
                return existing_topic, False

            existing_topic.title = title
            existing_topic.raw_content = raw_content
            existing_topic.clean_content = clean_content
            existing_topic.content_hash = content_hash
            existing_topic.author = author
            existing_topic.last_update_at = last_update_at
            existing_topic.scraped_at = datetime.utcnow()
            existing_topic.enriched = False
            existing_topic.is_closed = is_closed
            if is_closed:
                existing_topic.closed_at = datetime.utcnow()
            else:
                existing_topic.closed_at = None
            if created_at:
                existing_topic.created_at = created_at
            if embedding:
                existing_topic.embedding = embedding

            await self.session.flush()
            logger.info(
                "Topic updated",
                extra={"external_id": external_id, "title": title[:50]},
            )
            return existing_topic, True

        new_topic = Topic(
            external_id=external_id,
            title=title,
            raw_content=raw_content,
            clean_content=clean_content,
            content_hash=content_hash,
            author=author,
            last_update_at=last_update_at,
            scraped_at=datetime.utcnow(),
            enriched=False,
            embedding=embedding,
            is_closed=is_closed,
            created_at=created_at,
            closed_at=datetime.utcnow() if is_closed else None,
        )
        self.session.add(new_topic)
        await self.session.flush()
        logger.info(
            "Topic created",
            extra={"external_id": external_id, "title": title[:50]},
        )
        return new_topic, True

    async def commit(self) -> None:
        await self.session.commit()
