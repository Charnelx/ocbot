import asyncio
from dataclasses import dataclass, field
from typing import List

from enrichment import embedder, extraction, repository
from enrichment.config import get_settings
from enrichment.logging import get_logger

logger = get_logger(__name__)

settings = get_settings()

_run_lock = asyncio.Lock()


def is_busy() -> bool:
    return _run_lock.locked()


@dataclass
class EnrichmentRunResult:
    requested: int
    processed: int
    succeeded: int
    failed: int
    skipped_empty: int


async def run_enrichment(limit: int) -> EnrichmentRunResult:
    if _run_lock.locked():
        raise RuntimeError("already running")

    await _run_lock.acquire()
    try:
        return await _process_batch(limit)
    finally:
        _run_lock.release()


async def _process_batch(limit: int) -> EnrichmentRunResult:
    topics = await repository.fetch_unenriched_topics(limit)

    if not topics:
        logger.info("enrichment_batch_empty")
        return EnrichmentRunResult(requested=limit, processed=0, succeeded=0, failed=0, skipped_empty=0)

    logger.info("enrichment_batch_start", topic_count=len(topics))

    result = EnrichmentRunResult(
        requested=limit,
        processed=len(topics),
        succeeded=0,
        failed=0,
        skipped_empty=0,
    )

    # Limit concurrency to avoid overwhelming the OpenAI rate limits
    semaphore = asyncio.Semaphore(settings.enrichment_concurrency)

    async def _bounded(topic):
        async with semaphore:
            await _process_single(topic, result)

    await asyncio.gather(*[_bounded(topic) for topic in topics])

    logger.info(
        "enrichment_batch_complete",
        processed=result.processed,
        succeeded=result.succeeded,
        failed=result.failed,
        skipped_empty=result.skipped_empty,
    )

    return result


async def _process_single(topic, result: EnrichmentRunResult) -> None:
    logger.info(
        "topic_processing_start",
        topic_id=topic.id,
        title=topic.title,
    )

    try:
        content = topic.clean_content[: settings.max_content_chars]

        extraction_result = await extraction.extract_items_from_topic(
            topic_id=topic.id,
            topic_title=topic.title,
            clean_content=content,
        )

        if not extraction_result.items:
            await repository.mark_topic_enriched_empty(topic)
            result.skipped_empty += 1
            return

        is_standalone = len(extraction_result.items) == 1

        texts = [item.raw_text_segment for item in extraction_result.items]
        embeddings = embedder.embed_batch(texts)

        await repository.replace_topic_items(topic, extraction_result.items, embeddings, is_standalone)
        result.succeeded += 1

    except Exception as exc:
        await repository.mark_topic_failed(topic, error=str(exc))
        result.failed += 1