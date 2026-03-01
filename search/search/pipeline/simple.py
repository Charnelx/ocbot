import time

from search.config import settings
from search.embedder import embed_query
from search.filters import SearchFilters
from search.logging import get_logger
from search.pipeline.schemas import SearchModeUsed, SearchResponse, SearchResultItem
from search.repository import search_items_latest, search_items_simple

logger = get_logger(__name__)


async def run_simple_search(query: str, filters: SearchFilters) -> SearchResponse:
    start_time = time.monotonic()

    if not query.strip():
        results, total_filtered, total_matches = await search_items_latest(filters)
        search_mode_used = SearchModeUsed.LATEST
    else:
        query_vec = embed_query(query)
        results, total_filtered, total_matches = await search_items_simple(
            query_vec=query_vec,
            query_text=query,
            filters=filters,
            min_similarity=settings.min_similarity,
        )
        search_mode_used = SearchModeUsed.SIMPLE

    search_result_items = []
    for result in results:
        score = max(0.0, min(1.0, 1.0 - result.distance))
        topic_url = result.external_id

        search_result_items.append(
            SearchResultItem(
                item_id=result.item_id,
                topic_id=result.topic_id,
                topic_url=topic_url,
                title=result.title,
                category=result.category,
                labels=result.labels,
                price=result.price,
                currency=result.currency,
                is_standalone=result.is_standalone,
                raw_text_segment=result.raw_text_segment,
                author=result.author,
                last_update_at=result.last_update_at,
                created_at=result.created_at,
                score=score,
            )
        )

    duration_ms = (time.monotonic() - start_time) * 1000

    logger.info(
        "simple_search_complete",
        search_mode=search_mode_used.value,
        total_filtered=total_filtered,
        total_matches=total_matches,
        result_count=len(search_result_items),
        duration_ms=round(duration_ms, 2),
    )

    return SearchResponse(
        total_matches=total_matches,
        total_filtered=total_filtered,
        search_mode_used=search_mode_used,
        results=search_result_items,
    )
