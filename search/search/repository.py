from dataclasses import dataclass
from datetime import datetime

from shared.db import async_session_factory
from shared.models import Item, Topic
from sqlalchemy import ARRAY, String, cast, func, literal, select, text

from search.filters import SearchFilters, build_filter_clauses, build_order_clause


def _get_topic_existence_filter() -> list:
    """Filter to exclude deleted and closed topics from search results."""
    return [
        Topic.is_deleted == False,  # noqa: E712
        Topic.is_closed == False,  # noqa: E712
    ]


@dataclass
class ItemResult:
    item_id: int
    topic_id: int
    external_id: str
    title: str
    raw_text_segment: str
    category: str
    labels: list[str]
    price: float | None
    currency: str | None
    is_standalone: bool
    author: str
    last_update_at: datetime
    created_at: datetime | None
    distance: float
    matched_count: int


async def search_items_simple(
    query_vec: list[float],
    query_text: str,
    filters: SearchFilters,
    min_similarity: float,
) -> tuple[list[ItemResult], int, int]:
    distance_expr = Item.embedding.cosine_distance(query_vec)
    distance_col = distance_expr.label("distance")
    similarity_expr = literal(1.0) - Item.embedding.cosine_distance(query_vec)
    similarity_floor = similarity_expr >= min_similarity
    filter_clauses = build_filter_clauses(filters, Item, Topic)

    ts_query = func.plainto_tsquery("english", query_text)
    ts_vector = func.to_tsvector("english", Item.raw_text_segment)
    fts_rank = func.ts_rank(ts_vector, ts_query).label("fts_rank")
    fts_match = ts_vector.op("@@")(ts_query)

    async with async_session_factory() as session:
        stmt = (
            select(
                Item.id.label("item_id"),
                Item.topic_id,
                Item.title,
                Item.raw_text_segment,
                Item.category,
                Item.labels,
                Item.price,
                Item.currency,
                Item.is_standalone,
                Topic.author,
                Topic.last_update_at.label("topic_last_update_at"),
                Topic.created_at.label("topic_created_at"),
                Topic.external_id,
                distance_col,
                fts_rank,
                literal(0).label("matched_count"),
            )
            .join(Topic, Item.topic_id == Topic.id)
            .where(
                similarity_floor,
                fts_match,
                *_get_topic_existence_filter(),
                *filter_clauses,
            )
            .order_by(*build_order_clause(filters, Item, Topic, distance_expr))
        )

        if filters.limit is not None:
            stmt = stmt.limit(filters.limit)

        stmt = stmt.offset(filters.offset)

        result = await session.execute(stmt)
        rows = result.all()

        count_filtered_stmt = (
            select(func.count())
            .select_from(Item)
            .join(Topic, Item.topic_id == Topic.id)
            .where(
                similarity_floor,
                fts_match,
                *_get_topic_existence_filter(),
                *filter_clauses,
            )
        )
        count_filtered_result = await session.execute(count_filtered_stmt)
        total_filtered = count_filtered_result.scalar() or 0

        count_matches_stmt = (
            select(func.count())
            .select_from(Item)
            .join(Topic, Item.topic_id == Topic.id)
            .where(similarity_floor, fts_match, *_get_topic_existence_filter())
        )
        count_matches_result = await session.execute(count_matches_stmt)
        total_matches = count_matches_result.scalar() or 0

    items = [
        ItemResult(
            item_id=row.item_id,
            topic_id=row.topic_id,
            external_id=row.external_id,
            title=row.title,
            raw_text_segment=row.raw_text_segment,
            category=row.category,
            labels=row.labels or [],
            price=float(row.price) if row.price else None,
            currency=row.currency,
            is_standalone=row.is_standalone,
            author=row.author,
            last_update_at=row.topic_last_update_at,
            created_at=row.topic_created_at,
            distance=row.distance,
            matched_count=row.matched_count,
        )
        for row in rows
    ]

    return items, total_filtered, total_matches


async def search_items_smart(
    query_vec: list[float],
    category: str,
    agent_labels: list[str],
    filters: SearchFilters,
    use_precision: bool = False,
) -> tuple[list[ItemResult], int, int]:
    agent_labels_arr = cast(agent_labels, ARRAY(String))
    distance_expr = Item.embedding.cosine_distance(query_vec)
    distance_col = distance_expr.label("distance")
    category_clause = Item.category == category
    filter_clauses = build_filter_clauses(filters, Item, Topic)

    overlap_clause = None if use_precision else Item.labels.op("&&")(agent_labels_arr)

    matched_count_expr = func.cardinality(
        func.array_intersection(Item.labels, agent_labels_arr)
    )
    matched_count_col = matched_count_expr.label("matched_count")

    where_clauses = [category_clause]
    if overlap_clause is not None:
        where_clauses.append(overlap_clause)
    where_clauses.extend(_get_topic_existence_filter())
    where_clauses.extend(filter_clauses)

    async with async_session_factory() as session:
        stmt = (
            select(
                Item.id.label("item_id"),
                Item.topic_id,
                Item.title,
                Item.raw_text_segment,
                Item.category,
                Item.labels,
                Item.price,
                Item.currency,
                Item.is_standalone,
                Topic.author,
                Topic.last_update_at.label("topic_last_update_at"),
                Topic.created_at.label("topic_created_at"),
                Topic.external_id,
                distance_col,
                matched_count_col,
            )
            .join(Topic, Item.topic_id == Topic.id)
            .where(*where_clauses)
            .order_by(
                *build_order_clause(
                    filters,
                    Item,
                    Topic,
                    distance_expr,
                    matched_count_expr,
                    agent_labels_arr,
                )
            )
        )

        if filters.limit is not None:
            stmt = stmt.limit(filters.limit)

        stmt = stmt.offset(filters.offset)

        result = await session.execute(stmt)
        rows = result.all()

        count_filtered_where = [category_clause]
        if overlap_clause is not None:
            count_filtered_where.append(overlap_clause)
        count_filtered_where.extend(_get_topic_existence_filter())
        count_filtered_where.extend(filter_clauses)

        count_filtered_stmt = (
            select(func.count())
            .select_from(Item)
            .join(Topic, Item.topic_id == Topic.id)
            .where(*count_filtered_where)
        )
        count_filtered_result = await session.execute(count_filtered_stmt)
        total_filtered = count_filtered_result.scalar() or 0

        count_matches_where = [category_clause]
        if overlap_clause is not None:
            count_matches_where.append(overlap_clause)
        count_matches_where.extend(_get_topic_existence_filter())

        count_matches_stmt = (
            select(func.count())
            .select_from(Item)
            .join(Topic, Item.topic_id == Topic.id)
            .where(*count_matches_where)
        )
        count_matches_result = await session.execute(count_matches_stmt)
        total_matches = count_matches_result.scalar() or 0

    items = [
        ItemResult(
            item_id=row.item_id,
            topic_id=row.topic_id,
            external_id=row.external_id,
            title=row.title,
            raw_text_segment=row.raw_text_segment,
            category=row.category,
            labels=row.labels or [],
            price=float(row.price) if row.price else None,
            currency=row.currency,
            is_standalone=row.is_standalone,
            author=row.author,
            last_update_at=row.topic_last_update_at,
            created_at=row.topic_created_at,
            distance=row.distance,
            matched_count=row.matched_count,
        )
        for row in rows
    ]

    return items, total_filtered, total_matches


@dataclass
class SearchStats:
    total_items: int
    avg_label_count: float
    max_idf: float


async def get_search_stats() -> SearchStats | None:
    async with async_session_factory() as session:
        result = await session.execute(
            text(
                "SELECT total_items, avg_label_count, max_idf "
                "FROM search_stats WHERE id = 1"
            )
        )
        row = result.fetchone()
        if row is None:
            return None
        return SearchStats(
            total_items=row.total_items,
            avg_label_count=row.avg_label_count,
            max_idf=row.max_idf,
        )


async def get_label_stats() -> dict[str, int]:
    async with async_session_factory() as session:
        result = await session.execute(text("SELECT label, df FROM label_stats"))
        return {row.label: row.df for row in result.fetchall()}
