import logging
import os
from typing import Annotated

from fastapi import BackgroundTasks, FastAPI
from pydantic import BaseModel, Field

from scraper.config import scraper_settings
from scraper.dependencies import (
    ForumClientDep,
    TopicEmbedderDep,
    TopicRepositoryDep,
)
from scraper.jobs.cleanup_stale_topics import cleanup_stale_topics
from scraper.service import ScrapingService

os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TQDM_DISABLE"] = "1"


def configure_logging() -> None:
    log_level = os.getenv("SCRAPER_LOG_LEVEL", "INFO").upper()
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logging.root.setLevel(log_level)
    logging.root.addHandler(handler)

    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("torch").setLevel(logging.WARNING)
    logging.getLogger("tqdm").setLevel(logging.WARNING)


configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="OCBot Scraper+Ingestion Service",
    description="Fetches forum topics, cleans content, generates embeddings, and stores in DB",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class ScrapeRequest(BaseModel):
    """Request body for triggering a scraping job."""

    page_count: Annotated[
        int | None,
        Field(
            ge=1,
            le=50,
            description="Number of forum index pages to scrape. Each page contains up to 40 topics.",
        ),
    ] = None
    bulk_size: Annotated[
        int | None,
        Field(
            ge=1,
            le=50,
            description="Concurrent HTTP requests when fetching topic content.",
        ),
    ] = None
    bulk_delay_ms: Annotated[
        int | None,
        Field(
            ge=0,
            le=60000,
            description="Delay in milliseconds between bulk request batches. Helps avoid rate limiting.",
        ),
    ] = None
    user_agent: Annotated[
        str | None,
        Field(
            description="Custom User-Agent header to use for HTTP requests. Defaults to a browser-like UA if not provided.",
        ),
    ] = None
    webhook_url: Annotated[
        str | None,
        Field(
            description="Webhook URL to call when scraping completes. If not provided, no webhook will be called.",
        ),
    ] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "page_count": 5,
                    "bulk_size": 10,
                    "bulk_delay_ms": 2000,
                },
                {
                    "page_count": 10,
                    "bulk_size": 5,
                    "bulk_delay_ms": 5000,
                    "user_agent": "Mozilla/5.0 (compatible; OCBot/1.0)",
                },
            ]
        }
    }


class ScrapeResponse(BaseModel):
    """Response from a scraping job trigger."""

    message: Annotated[str, Field(description="Human-readable status message")]
    page_count: Annotated[int, Field(description="Number of pages that will be scraped")]


@app.get(
    "/health",
    tags=["Health"],
    summary="Health check endpoint",
    description="Returns the health status of the service. Use this to verify the service is running.",
)
async def health_check() -> dict:
    """Check service health status."""
    return {"status": "healthy"}


async def _call_webhook(webhook_url: str | None, payload: dict) -> None:
    """Call a webhook URL with the given payload."""
    if not webhook_url:
        return

    import httpx

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.post(webhook_url, json=payload)
        logger.info("Webhook called", extra={"webhook_url": webhook_url, "status": payload.get("status")})
    except Exception as e:
        logger.warning("Webhook call failed", extra={"webhook_url": webhook_url, "error": str(e)})


async def run_scraping_task(
    page_count: int,
    bulk_size: int,
    bulk_delay_ms: int,
    user_agent: str,
    webhook_url: str | None,
    client: ForumClientDep,
    embedder: TopicEmbedderDep,
    repository: TopicRepositoryDep,
) -> None:
    """Background task that runs the scraping workflow."""
    service = ScrapingService(
        client=client,
        embedder=embedder,
        repository=repository,
    )

    try:
        result = await service.run(
            page_count=page_count,
            bulk_size=bulk_size,
            bulk_delay_ms=bulk_delay_ms,
            user_agent=user_agent,
        )

        logger.info(
            "Scraping task completed",
            extra={
                "processed": result.processed_count,
                "skipped": result.skipped_count,
            },
        )

        await _call_webhook(
            webhook_url,
            {
                "status": "success",
                "service": "scraper",
                "processed_count": result.processed_count,
                "skipped_count": result.skipped_count,
                "error": None,
            },
        )
    except Exception as e:
        logger.error("Scraping task failed", extra={"error": str(e)}, exc_info=True)
        await _call_webhook(
            webhook_url,
            {
                "status": "error",
                "service": "scraper",
                "processed_count": 0,
                "skipped_count": 0,
                "error": str(e),
            },
        )


@app.post(
    "/scrape",
    response_model=ScrapeResponse,
    tags=["Scraping"],
    summary="Trigger a scraping job",
    description=(
        "Initiates a background scraping job that fetches forum topics, cleans content, "
        "generates embeddings, and stores results in the database. The request returns "
        "immediately while the actual scraping runs asynchronously.\n\n"
        "Use this endpoint to trigger periodic scraping via an external scheduler (e.g., n8n)."
    ),
    status_code=202,
)
async def scrape_topics(
    request: ScrapeRequest,
    background_tasks: BackgroundTasks,
    client: ForumClientDep,
    embedder: TopicEmbedderDep,
    repository: TopicRepositoryDep,
) -> ScrapeResponse:
    page_count = request.page_count or scraper_settings.default_page_count
    bulk_size = request.bulk_size or scraper_settings.default_bulk_size
    bulk_delay_ms = request.bulk_delay_ms or scraper_settings.default_bulk_delay_ms
    user_agent = request.user_agent or scraper_settings.default_user_agent
    webhook_url = request.webhook_url or scraper_settings.webhook_url

    logger.info(
        "Scrape request received",
        extra={
            "page_count": page_count,
            "bulk_size": bulk_size,
            "bulk_delay_ms": bulk_delay_ms,
        },
    )

    background_tasks.add_task(
        run_scraping_task,
        page_count=page_count,
        bulk_size=bulk_size,
        bulk_delay_ms=bulk_delay_ms,
        user_agent=user_agent,
        webhook_url=webhook_url,
        client=client,
        embedder=embedder,
        repository=repository,
    )

    return ScrapeResponse(message="Scraping started", page_count=page_count)


class CleanupStaleTopicsResponse(BaseModel):
    """Response from cleanup stale topics job."""

    message: Annotated[str, Field(description="Human-readable status message")]
    topics_checked: Annotated[int, Field(description="Number of topics checked")]
    topics_deleted: Annotated[int, Field(description="Number of topics marked as deleted")]
    topics_closed: Annotated[int, Field(description="Number of topics marked as closed")]
    topics_reopened: Annotated[int, Field(description="Number of topics reopened")]


async def run_cleanup_task(stale_days: int | None) -> CleanupStaleTopicsResponse:
    """Background task that runs the stale topic cleanup."""
    result = await cleanup_stale_topics(stale_days)
    return CleanupStaleTopicsResponse(
        message=result.message,
        topics_checked=result.topics_checked,
        topics_deleted=result.topics_deleted,
        topics_closed=result.topics_closed,
        topics_reopened=result.topics_reopened,
    )


@app.post(
    "/cleanup-stale-topics",
    response_model=CleanupStaleTopicsResponse,
    tags=["Maintenance"],
    summary="Clean up stale topics",
    description=(
        "Checks topics that haven't been updated in a while and verifies if they still exist. "
        "Marks topics as deleted (404) or closed (topic_read_locked class). "
        "Also reopens topics if they become available again.\n\n"
        "Use this endpoint to periodically clean up deleted/closed topics via an external scheduler (e.g., n8n)."
    ),
    status_code=202,
)
async def cleanup_stale_topics_endpoint(
    background_tasks: BackgroundTasks,
    stale_days: Annotated[
        int | None,
        Field(
            ge=1,
            le=365,
            description="Number of days after which a topic is considered stale. Defaults to config value.",
        ),
    ] = None,
) -> CleanupStaleTopicsResponse:
    stale_days = stale_days or scraper_settings.stale_topic_days

    logger.info(
        "Cleanup stale topics request received",
        extra={"stale_days": stale_days},
    )

    background_tasks.add_task(run_cleanup_task, stale_days)

    return CleanupStaleTopicsResponse(
        message="Cleanup started",
        topics_checked=0,
        topics_deleted=0,
        topics_closed=0,
        topics_reopened=0,
    )


if __name__ == "__main__":
    import asyncio

    import uvicorn

    config = uvicorn.Config("scraper.main:app", host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)
    asyncio.run(server.serve())
