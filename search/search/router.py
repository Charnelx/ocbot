from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Query
from pydantic import BaseModel
from sqlalchemy import func, select

from search.config import settings
from search.filters import SortOrder, from_query_params
from search.jobs.cleanup_labels import cleanup_labels
from search.jobs.recompute_stats import recompute_stats
from search.logging import get_logger
from search.pipeline import run_simple_search, run_smart_search
from search.pipeline.schemas import SearchResponse
from shared.db import async_session_factory
from shared.models import Topic

logger = get_logger(__name__)

router = APIRouter()


class HealthResponse(BaseModel):
    status: str


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="healthy")


class StatsResponse(BaseModel):
    last_scrape_at: datetime | None = None


@router.get("/api/stats", response_model=StatsResponse)
async def get_stats() -> StatsResponse:
    async with async_session_factory() as session:
        result = await session.execute(select(func.max(Topic.scraped_at)))
        last_scrape_at = result.scalar_one_or_none()
    return StatsResponse(last_scrape_at=last_scrape_at)


@router.get("/api/search", response_model=SearchResponse)
async def search(
    q: str = Query(default="", max_length=settings.max_query_chars),
    mode: Literal["simple", "smart"] = "simple",
    category: list[str] | None = Query(default=None),  # noqa: B008
    price_min: float | None = Query(default=None, ge=0),  # noqa: B008
    price_max: float | None = Query(default=None, ge=0),  # noqa: B008
    currency: Literal["UAH", "USD", "any"] | None = Query(default=None),  # noqa: B008
    standalone_only: bool = False,
    date_from: datetime | None = Query(default=None),  # noqa: B008
    date_to: datetime | None = Query(default=None),  # noqa: B008
    sort: SortOrder = SortOrder.RELEVANCE,
    limit: int | None = Query(default=None, ge=1),  # noqa: B008
    offset: int | None = Query(default=None, ge=0),  # noqa: B008
    min_score: float | None = Query(default=0.6, ge=0.1, le=1.0),  # noqa: B008
    score_auto_tune: bool = False,
) -> SearchResponse:
    logger.info(
        "search_request",
        query_len=len(q),
        mode=mode,
        limit=limit,
        offset=offset or 0,
    )

    filters = from_query_params(
        categories=category,
        price_min=price_min,
        price_max=price_max,
        currency=currency,
        standalone_only=standalone_only,
        date_from=date_from,
        date_to=date_to,
        sort=sort,
        limit=limit,
        offset=offset,
        min_score=min_score,
        score_auto_tune=score_auto_tune,
    )

    if mode == "smart":
        return await run_smart_search(q, filters)
    else:
        return await run_simple_search(q, filters)


class RecomputeStatsResponse(BaseModel):
    success: bool
    total_items: int
    avg_label_count: float
    unique_labels: int
    max_idf: float
    message: str


@router.post("/maintenance/recompute-stats", response_model=RecomputeStatsResponse)
async def maintenance_recompute_stats() -> RecomputeStatsResponse:
    result = await recompute_stats()
    return RecomputeStatsResponse(
        success=result.success,
        total_items=result.total_items,
        avg_label_count=result.avg_label_count,
        unique_labels=result.unique_labels,
        max_idf=result.max_idf,
        message=result.message,
    )


class CleanupLabelsResponse(BaseModel):
    items_cleaned: int
    items_deleted: int


@router.post("/maintenance/cleanup-labels", response_model=CleanupLabelsResponse)
async def maintenance_cleanup_labels() -> CleanupLabelsResponse:
    result = await cleanup_labels()
    return CleanupLabelsResponse(
        items_cleaned=result.items_cleaned,
        items_deleted=result.items_deleted,
    )
