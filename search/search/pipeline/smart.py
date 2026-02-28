import asyncio
import time
from math import log

from search.config import settings
from search.embedder import embed_query
from search.filters import SearchFilters
from search.logging import get_logger
from search.pipeline.agent import classify_query
from search.pipeline.schemas import (
    AgentClassification,
    ItemCategory,
    SearchModeUsed,
    SearchResponse,
    SearchResultItem,
)
from search.pipeline.simple import run_simple_search
from search.repository import get_label_stats, get_search_stats, search_items_smart

logger = get_logger(__name__)

DEFAULT_MIN_SCORE = 0.6


def _apply_recall_scoring(
    label_match_ratio: float,
    cosine_sim: float,
) -> float:
    """
    Apply recall-mode scoring: simple weighted combination of label match ratio
    and cosine similarity.

    Formula:
        score = score_weight_labels * label_match_ratio +
                score_weight_cosine * cosine_sim

    Args:
        label_match_ratio: Ratio of agent labels that match item labels
        cosine_sim: Cosine similarity between query and item embeddings (0-1)

    Returns:
        Combined score in range [0, 1]
    """
    return (
        settings.score_weight_labels * label_match_ratio
        + settings.score_weight_cosine * cosine_sim
    )


def _apply_precision_scoring(
    agent_labels: list[str],
    item_labels: list[str],
    cosine_sim: float,
    label_df: dict[str, int],
    total_items: int,
    avg_label_count: float,
    max_idf: float,
) -> float:
    """
    Apply precision-mode scoring: IDF-weighted hybrid scoring with soft regularization.

    This scoring method addresses limitations of simple recall scoring by:
    1. Using IDF-weighted containment to boost discriminative labels
    2. Applying soft length regularization to penalize label spam
    3. Adapting label vs embedding weights based on query specificity

    Formula:
        S_labels = sum(idf_norm(l) for l in A ∩ B) / sum(idf_norm(l) for l in A)
        L = 1 / (1 + α * max(0, |B| - μ))  # length regularization
        S_labels_final = S_labels * L
        specificity = (1/|A|) * sum(idf_norm(l) for l in A)
        w_labels = 0.4 + 0.4 * specificity
        w_cosine = 1 - w_labels
        score = w_labels * S_labels_final + w_cosine * cosine_sim

    Args:
        agent_labels: Labels extracted from query by agent
        item_labels: Labels associated with item from enrichment
        cosine_sim: Cosine similarity between query and item embeddings (0-1)
        label_df: Dictionary mapping label -> document frequency
        total_items: Total number of items in database
        avg_label_count: Average number of labels per item
        max_idf: Maximum IDF value across all labels (for normalization)

    Returns:
        Combined score in range [0, 1]
    """
    if not agent_labels:
        return cosine_sim

    idf_norm: dict[str, float] = {}
    for label in agent_labels:
        df = label_df.get(label, 1)
        idf = log(1 + total_items / df)
        idf_norm[label] = idf / max_idf if max_idf > 0 else 1.0

    intersection = set(agent_labels) & set(item_labels)

    if not intersection:
        s_labels = 0.0
    else:
        numerator = sum(idf_norm.get(label, 1.0) for label in intersection)
        denominator = sum(idf_norm.get(label, 1.0) for label in agent_labels)
        s_labels = numerator / denominator if denominator > 0 else 0.0

    regularization_alpha = 0.1
    length_penalty = 1.0 / (
        1.0 + regularization_alpha * max(0, len(item_labels) - avg_label_count)
    )
    s_labels_final = s_labels * length_penalty

    specificity = (
        (1.0 / len(agent_labels)) * sum(idf_norm.values()) if agent_labels else 0.0
    )

    w_labels = 0.4 + 0.4 * specificity
    w_cosine = 1.0 - w_labels

    score = w_labels * s_labels_final + w_cosine * cosine_sim

    return max(0.0, min(1.0, score))


def _is_low_confidence(classification: AgentClassification) -> bool:
    """Check if agent classification confidence is too low for smart search."""
    score_too_low = classification.confidence < settings.confidence_threshold
    quality_bad = (
        classification.category == ItemCategory.OTHER
        and len(classification.labels) <= 1
    )
    return score_too_low or quality_bad


async def _search_with_threshold(
    query_vec: list[float],
    category: str,
    agent_labels: list[str],
    filters: SearchFilters,
    use_precision: bool,
    threshold: float,
    search_stats,
    label_df: dict[str, int],
) -> tuple[list[SearchResultItem], int, int]:
    """
    Execute search and filter results by score threshold.

    Args:
        query_vec: Embedded query vector
        category: Item category to filter by
        agent_labels: Labels from agent classification
        filters: Search filters
        use_precision: Whether to use precision ranking algorithm
        threshold: Minimum score threshold
        search_stats: Statistics for precision scoring
        label_df: Label document frequencies for precision scoring

    Returns:
        Tuple of (filtered_results, total_filtered, total_matches)
    """
    results, total_filtered, total_matches = await search_items_smart(
        query_vec=query_vec,
        category=category,
        agent_labels=agent_labels,
        filters=filters,
        use_precision=use_precision,
    )

    search_result_items = []
    for result in results:
        cosine_sim = max(0.0, min(1.0, 1.0 - result.distance))

        if use_precision and search_stats is not None:
            score = _apply_precision_scoring(
                agent_labels=agent_labels,
                item_labels=result.labels,
                cosine_sim=cosine_sim,
                label_df=label_df,
                total_items=search_stats.total_items,
                avg_label_count=search_stats.avg_label_count,
                max_idf=search_stats.max_idf,
            )
        else:
            label_match_ratio = (
                result.matched_count / len(agent_labels) if agent_labels else 0.0
            )
            score = _apply_recall_scoring(label_match_ratio, cosine_sim)

        if score < threshold:
            continue

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

    return search_result_items, total_filtered, total_matches


async def _agent_pipeline(query: str, filters: SearchFilters) -> SearchResponse:
    classification = await classify_query(query)

    if _is_low_confidence(classification):
        logger.info(
            "smart_confidence_low",
            confidence=classification.confidence,
            category=classification.category.value,
            labels_count=len(classification.labels),
            trigger="low_confidence",
        )
        response = await run_simple_search(query, filters)
        return response.model_copy(
            update={"search_mode_used": SearchModeUsed.SMART_FALLBACK}
        )

    query_vec = embed_query(query)

    use_precision = settings.ranking_algorithm == "precision"

    search_stats = None
    label_df: dict[str, int] = {}

    if use_precision:
        search_stats = await get_search_stats()
        label_df = await get_label_stats()

        if search_stats is None or not label_df:
            logger.warning(
                "precision_ranking_stats_unavailable",
                search_stats_available=search_stats is not None,
                label_stats_available=bool(label_df),
            )
            use_precision = False
        else:
            logger.debug(
                "precision_ranking_stats_loaded",
                total_items=search_stats.total_items,
                avg_label_count=search_stats.avg_label_count,
                max_idf=search_stats.max_idf,
                unique_labels=len(label_df),
            )

    if filters.score_auto_tune:
        threshold = DEFAULT_MIN_SCORE
        agent_label_count = len(classification.labels)
        search_result_items: list[SearchResultItem] = []
        total_matches = 0
        auto_tuned_threshold: float | None = None

        logger.info(
            "score_auto_tune_started",
            initial_threshold=threshold,
            agent_label_count=agent_label_count,
        )

        while threshold > 0:
            (
                search_result_items,
                total_filtered,
                total_matches,
            ) = await _search_with_threshold(
                query_vec=query_vec,
                category=classification.category.value,
                agent_labels=classification.labels,
                filters=filters,
                use_precision=use_precision,
                threshold=threshold,
                search_stats=search_stats,
                label_df=label_df,
            )

            if search_result_items:
                auto_tuned_threshold = threshold
                logger.info(
                    "score_auto_tune_found",
                    threshold=threshold,
                    result_count=len(search_result_items),
                )
                break

            threshold -= settings.score_auto_tune_step

        if not search_result_items:
            logger.info(
                "score_auto_tune_no_results",
                final_threshold=threshold,
            )

        return SearchResponse(
            total_matches=total_matches,
            total_filtered=len(search_result_items),
            search_mode_used=SearchModeUsed.SMART,
            results=search_result_items,
            identified_category=classification.category.value,
            identified_labels=classification.labels,
            auto_tuned_threshold=auto_tuned_threshold,
        )

    results, total_filtered, total_matches = await _search_with_threshold(
        query_vec=query_vec,
        category=classification.category.value,
        agent_labels=classification.labels,
        filters=filters,
        use_precision=use_precision,
        threshold=filters.min_score if filters.min_score is not None else 0.0,
        search_stats=search_stats,
        label_df=label_df,
    )

    return SearchResponse(
        total_matches=total_matches,
        total_filtered=len(results),
        search_mode_used=SearchModeUsed.SMART,
        results=results,
        identified_category=classification.category.value,
        identified_labels=classification.labels,
    )


async def run_smart_search(query: str, filters: SearchFilters) -> SearchResponse:
    start_time = time.monotonic()

    try:
        response = await asyncio.wait_for(
            _agent_pipeline(query, filters),
            timeout=settings.smart_timeout_seconds,
        )
    except TimeoutError:
        logger.warning("smart_fallback_triggered", reason="timeout")
        response = await run_simple_search(query, filters)
        response = response.model_copy(
            update={"search_mode_used": SearchModeUsed.SMART_FALLBACK}
        )
    except Exception as exc:
        logger.warning(
            "smart_fallback_triggered",
            reason="llm_error",
            error=str(exc),
            exc_info=True,
        )
        response = await run_simple_search(query, filters)
        response = response.model_copy(
            update={"search_mode_used": SearchModeUsed.SMART_FALLBACK}
        )

    duration_seconds = time.monotonic() - start_time
    response.search_time_seconds = round(duration_seconds, 2)

    logger.info(
        "smart_search_complete",
        total_filtered=response.total_filtered,
        total_matches=response.total_matches,
        result_count=len(response.results),
        search_mode_used=response.search_mode_used.value,
        duration_seconds=round(duration_seconds, 2),
    )

    return response
