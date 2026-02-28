import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from scraper.exceptions import (
    ContentCleanError,
    DatabaseError,
    EmbeddingError,
    ForumFetchError,
    TopicParseError,
)
from scraper.ingestion.cleaner import clean_content
from scraper.ingestion.embedder import TopicEmbedder
from scraper.ingestion.hasher import compute_hash
from scraper.repository import TopicRepository
from scraper.scraper.client import ForumClient, TopicSummary
from scraper.scraper.parser import parse_forum_index, parse_topic_page

logger = logging.getLogger(__name__)


@dataclass
class ScrapingResult:
    """Result of a scraping operation."""

    processed_count: int
    skipped_count: int
    total_duration_sec: float


class ScrapingService:
    """Service for orchestrating the scraping workflow."""

    def __init__(
        self,
        client: ForumClient,
        embedder: TopicEmbedder,
        repository: TopicRepository,
    ) -> None:
        self.client = client
        self.embedder = embedder
        self.repository = repository

    async def run(
        self,
        page_count: int,
        bulk_size: int,
        bulk_delay_ms: int,
        user_agent: str,
    ) -> ScrapingResult:
        """Execute the full scraping workflow."""
        total_start = time.time()

        logger.info(
            "Starting scraping job",
            extra={
                "page_count": page_count,
                "bulk_size": bulk_size,
                "bulk_delay_ms": bulk_delay_ms,
            },
        )

        try:
            topics = await self._fetch_forum_topics(page_count)

            if bulk_delay_ms > 0:
                await asyncio.sleep(bulk_delay_ms / 1000.0)

            topic_contents = await self._fetch_topic_contents(topics)
            processed_topics = self._process_contents(topics, topic_contents)
            embeddings = self._generate_embeddings(processed_topics)
            result = await self._save_to_db(processed_topics, embeddings)
        finally:
            await self.client.close()

        total_time = time.time() - total_start
        result.total_duration_sec = total_time

        logger.info(
            "Scraping job complete",
            extra={
                "processed": result.processed_count,
                "skipped": result.skipped_count,
                "total_duration_sec": total_time,
            },
        )

        return result

    async def _fetch_forum_topics(self, page_count: int) -> list[TopicSummary]:
        """Fetch and parse topics from forum index pages."""
        logger.info("Fetching forum index pages")
        fetch_start = time.time()

        try:
            html_pages = await self.client.fetch_forum_index(page_count)
        except Exception as e:
            raise ForumFetchError(f"Failed to fetch forum index: {e}") from e

        fetch_time = time.time() - fetch_start
        logger.info(
            "Forum index pages fetched",
            extra={"page_count": len(html_pages), "duration_sec": fetch_time},
        )

        all_topics: list[TopicSummary] = []
        for html in html_pages:
            try:
                topics = parse_forum_index(html)
                all_topics.extend(topics)
            except Exception as e:
                raise TopicParseError(f"Failed to parse forum HTML: {e}") from e

        logger.info(
            "Topics parsed from index",
            extra={"topic_count": len(all_topics)},
        )

        return all_topics

    async def _fetch_topic_contents(
        self,
        topics: list[TopicSummary],
    ) -> dict[str, str]:
        """Fetch raw HTML content for each topic."""
        logger.info("Fetching topic content pages")
        content_start = time.time()

        topic_contents = await self.client.fetch_topics_content(topics)

        content_time = time.time() - content_start
        logger.info(
            "Topic content fetched",
            extra={
                "topic_count": len(topic_contents),
                "duration_sec": content_time,
            },
        )

        return topic_contents

    def _process_contents(
        self,
        topics: list[TopicSummary],
        contents: dict[str, str],
    ) -> list[dict[str, Any]]:
        """Clean content and prepare topics for embedding."""
        logger.info("Cleaning and hashing content")
        clean_start = time.time()

        processed_topics: list[dict[str, Any]] = []
        texts_to_embed: list[str] = []

        for topic in topics:
            raw_html = contents.get(topic.external_id, "")
            if not raw_html:
                logger.warning(
                    "No content found for topic",
                    extra={"external_id": topic.external_id},
                )
                continue

            try:
                topic_data = parse_topic_page(raw_html)
                raw_content = topic_data.raw_html
                created_at = topic_data.created_at
            except Exception as e:
                raise TopicParseError(f"Failed to parse topic content for {topic.external_id}: {e}") from e

            try:
                clean_text = clean_content(raw_content)
            except Exception as e:
                raise ContentCleanError(f"Failed to clean content for {topic.external_id}: {e}") from e

            content_hash = compute_hash(clean_text)

            last_update = self._parse_datetime(topic.last_update_at)
            topic_created_at = self._parse_datetime(created_at) if created_at else None

            processed_topics.append(
                {
                    "external_id": topic.external_id,
                    "title": topic.title,
                    "raw_content": raw_content,
                    "clean_content": clean_text,
                    "content_hash": content_hash,
                    "author": topic.author,
                    "last_update_at": last_update,
                    "created_at": topic_created_at,
                    "is_closed": topic.is_closed,
                }
            )
            texts_to_embed.append(clean_text)

        clean_time = time.time() - clean_start
        logger.info(
            "Content cleaned and hashed",
            extra={
                "topic_count": len(processed_topics),
                "duration_sec": clean_time,
            },
        )

        return processed_topics

    def _generate_embeddings(
        self,
        topics: list[dict[str, Any]],
    ) -> list[list[float]]:
        """Generate embeddings for topic content."""
        if not topics:
            return []

        logger.info("Generating embeddings")
        embed_start = time.time()

        texts = [topic["clean_content"] for topic in topics]

        try:
            embeddings = self.embedder.embed(texts)
        except Exception as e:
            raise EmbeddingError(f"Failed to generate embeddings: {e}") from e

        embed_time = time.time() - embed_start
        logger.info(
            "Embeddings generated",
            extra={
                "count": len(embeddings),
                "duration_sec": embed_time,
            },
        )

        return embeddings

    async def _save_to_db(
        self,
        topics: list[dict[str, Any]],
        embeddings: list[list[float]],
    ) -> ScrapingResult:
        """Save topics to database."""
        logger.info("Upserting topics to database")
        db_start = time.time()

        processed_count = 0
        skipped_count = 0

        try:
            for i, topic_data in enumerate(topics):
                embedding = embeddings[i] if i < len(embeddings) else None
                _, created = await self.repository.upsert_topic(
                    external_id=topic_data["external_id"],
                    title=topic_data["title"],
                    raw_content=topic_data["raw_content"],
                    clean_content=topic_data["clean_content"],
                    content_hash=topic_data["content_hash"],
                    author=topic_data["author"],
                    last_update_at=topic_data["last_update_at"],
                    embedding=embedding,
                    is_closed=topic_data.get("is_closed", False),
                    created_at=topic_data.get("created_at"),
                )
                if created:
                    processed_count += 1
                else:
                    skipped_count += 1

            await self.repository.commit()
        except Exception as e:
            raise DatabaseError(f"Failed to save topics to database: {e}") from e

        db_time = time.time() - db_start
        logger.info(
            "Topics saved to DB",
            extra={
                "processed": processed_count,
                "skipped": skipped_count,
                "duration_sec": db_time,
            },
        )

        return ScrapingResult(
            processed_count=processed_count,
            skipped_count=skipped_count,
            total_duration_sec=0.0,
        )

    def _parse_datetime(self, date_str: str | None) -> datetime:
        """Parse datetime string to datetime object."""
        if not date_str:
            return datetime.utcnow()

        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except ValueError:
            return datetime.utcnow()
