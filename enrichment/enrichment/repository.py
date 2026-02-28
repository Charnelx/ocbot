from decimal import Decimal

from shared.db import async_session_factory
from shared.models import Item, Topic
from sqlalchemy import delete, select, update

from enrichment.config import get_settings
from enrichment.extraction.schemas import ExtractedItem
from enrichment.logging import get_logger

logger = get_logger(__name__)

settings = get_settings()


async def fetch_unenriched_topics(limit: int) -> list[Topic]:
    async with async_session_factory() as session:
        result = await session.execute(
            select(Topic)
            .where(Topic.enriched.is_(False))
            .where(Topic.enrichment_attempts < settings.max_topic_attempts)
            .order_by(Topic.scraped_at.asc())
            .limit(limit)
        )
        topics = list(result.scalars().all())
        return topics


async def replace_topic_items(
    topic: Topic,
    extracted_items: list[ExtractedItem],
    embeddings: list[list[float]],
    is_standalone: bool,
) -> None:
    async with async_session_factory() as session:
        await session.execute(delete(Item).where(Item.topic_id == topic.id))

        for extracted_item, embedding in zip(extracted_items, embeddings, strict=True):
            labels = list(dict.fromkeys(extracted_item.labels))
            item = Item(
                topic_id=topic.id,
                title=extracted_item.title,
                raw_text_segment=extracted_item.raw_text_segment,
                category=extracted_item.category.value,
                labels=labels,
                price=Decimal(str(extracted_item.price)) if extracted_item.price else None,
                currency=extracted_item.currency.value if extracted_item.currency else "UAH",
                embedding=embedding,
                is_standalone=is_standalone,
            )
            session.add(item)

        await session.execute(update(Topic).where(Topic.id == topic.id).values(enriched=True, enrichment_error=None))
        await session.commit()

        logger.info(
            "topic_enriched",
            topic_id=topic.id,
            items_written=len(extracted_items),
            is_standalone=is_standalone,
        )


async def mark_topic_enriched_empty(topic: Topic) -> None:
    async with async_session_factory() as session:
        await session.execute(delete(Item).where(Item.topic_id == topic.id))
        await session.execute(update(Topic).where(Topic.id == topic.id).values(enriched=True, enrichment_error=None))
        await session.commit()

        logger.warning(
            "topic_enriched_no_items",
            topic_id=topic.id,
            topic_title=topic.title,
        )


async def mark_topic_failed(topic: Topic, error: str) -> None:
    error_truncated = error[:1000]
    async with async_session_factory() as session:
        await session.execute(
            update(Topic)
            .where(Topic.id == topic.id)
            .values(
                enrichment_attempts=Topic.enrichment_attempts + 1,
                enrichment_error=error_truncated,
            )
        )
        await session.commit()

        logger.error(
            "topic_enrichment_failed",
            topic_id=topic.id,
            attempts=topic.enrichment_attempts + 1,
            error=error_truncated,
        )
