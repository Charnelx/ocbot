from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

from curl_cffi.requests import AsyncSession
from sqlalchemy import select

from scraper.config import scraper_settings
from shared.db import async_session_factory
from shared.models.topic import Topic

logger = logging.getLogger(__name__)


@dataclass
class CleanupResult:
    success: bool
    topics_checked: int
    topics_deleted: int
    topics_closed: int
    topics_reopened: int
    message: str


async def cleanup_stale_topics(stale_days: int | None = None) -> CleanupResult:
    """
    Check topics that haven't been updated in stale_days and verify if they still exist.

    For each stale topic:
    - GET the topic URL
    - If 404: mark is_deleted=true, deleted_at=now()
    - If 200 and has 'topic_read_locked' class: mark is_closed=true, closed_at=now()
    - If 200 and no closed marker (topic reopened):
        mark is_deleted=false, is_closed=false, deleted_at=null, closed_at=null
    """
    effective_stale_days = stale_days or scraper_settings.stale_topic_days
    cutoff_date = datetime.utcnow() - timedelta(days=effective_stale_days)

    async with async_session_factory() as session:
        stmt = (
            select(Topic)
            .where(
                Topic.is_deleted == False,  # noqa: E712
                Topic.last_update_at < cutoff_date,
            )
            .limit(100)
        )
        result = await session.execute(stmt)
        stale_topics = result.scalars().all()

        if not stale_topics:
            logger.info("No stale topics found to check")
            return CleanupResult(
                success=True,
                topics_checked=0,
                topics_deleted=0,
                topics_closed=0,
                topics_reopened=0,
                message="No stale topics found",
            )

        logger.info(
            "Checking stale topics",
            extra={"topic_count": len(stale_topics), "cutoff_date": cutoff_date.isoformat()},
        )

        client = AsyncSession(
            timeout=30,
            impersonate="chrome120",
            allow_redirects=True,
        )

        topics_deleted = 0
        topics_closed = 0
        topics_reopened = 0

        try:
            for topic in stale_topics:
                topic_url = f"{topic.external_id}"

                try:
                    response = await client.get(topic_url)

                    if response.status_code == 404:
                        topic.is_deleted = True
                        topic.deleted_at = datetime.utcnow()
                        topics_deleted += 1
                        logger.debug(
                            "Topic marked as deleted",
                            extra={"external_id": topic.external_id},
                        )

                    elif response.status_code == 200:
                        html = response.text
                        if "topic_read_locked" in html or "topic_read_hot_locked" in html:
                            if not topic.is_closed:
                                topic.is_closed = True
                                topic.closed_at = datetime.utcnow()
                                topics_closed += 1
                                logger.debug(
                                    "Topic marked as closed",
                                    extra={"external_id": topic.external_id},
                                )
                        else:
                            if topic.is_deleted or topic.is_closed:
                                topic.is_deleted = False
                                topic.is_closed = False
                                topic.deleted_at = None
                                topic.closed_at = None
                                topics_reopened += 1
                                logger.debug(
                                    "Topic reopened",
                                    extra={"external_id": topic.external_id},
                                )

                except Exception as e:
                    logger.warning(
                        "Failed to check topic",
                        extra={"external_id": topic.external_id, "error": str(e)},
                    )

                await session.flush()

            await session.commit()

        finally:
            await client.close()

        logger.info(
            "Stale topics cleanup complete",
            extra={
                "topics_checked": len(stale_topics),
                "topics_deleted": topics_deleted,
                "topics_closed": topics_closed,
                "topics_reopened": topics_reopened,
            },
        )

        return CleanupResult(
            success=True,
            topics_checked=len(stale_topics),
            topics_deleted=topics_deleted,
            topics_closed=topics_closed,
            topics_reopened=topics_reopened,
            message=(
                f"Checked {len(stale_topics)} topics: "
                f"{topics_deleted} deleted, {topics_closed} closed, {topics_reopened} reopened"
            ),
        )
