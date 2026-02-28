from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from sqlalchemy import func

from search.config import settings


class SortOrder(str, Enum):  # noqa: UP042
    RELEVANCE = "relevance"
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"
    NEWEST = "newest"
    OLDEST = "oldest"
    UPDATED = "updated"


@dataclass
class SearchFilters:
    categories: list[str] | None = None
    price_min: float | None = None
    price_max: float | None = None
    currency: str | None = None
    standalone_only: bool = False
    date_from: datetime | None = None
    date_to: datetime | None = None
    sort: SortOrder = SortOrder.RELEVANCE
    limit: int | None = None
    offset: int = 0
    min_score: float | None = None
    score_auto_tune: bool = False

    def __post_init__(self) -> None:
        if self.limit is not None:
            if self.limit < 1:
                self.limit = 1
            elif self.limit > settings.max_limit:
                self.limit = settings.max_limit

        if self.offset < 0:
            self.offset = 0


def from_query_params(
    categories: list[str] | None = None,
    price_min: float | None = None,
    price_max: float | None = None,
    currency: str | None = None,
    standalone_only: bool = False,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    sort: SortOrder = SortOrder.RELEVANCE,
    limit: int | None = None,
    offset: int | None = None,
    min_score: float | None = None,
    score_auto_tune: bool = False,
) -> SearchFilters:
    return SearchFilters(
        categories=categories,
        price_min=price_min,
        price_max=price_max,
        currency=currency,
        standalone_only=standalone_only,
        date_from=date_from,
        date_to=date_to,
        sort=sort,
        limit=limit,
        offset=offset if offset is not None else 0,
        min_score=min_score,
        score_auto_tune=score_auto_tune,
    )


def build_filter_clauses(
    filters: SearchFilters,
    Item: type,
    Topic: type,
) -> list:
    clauses = []

    if filters.categories is not None:
        clauses.append(Item.category.in_(filters.categories))

    if filters.price_min is not None:
        clauses.append(Item.price >= filters.price_min)

    if filters.price_max is not None:
        clauses.append(Item.price <= filters.price_max)

    if filters.currency is not None and filters.currency != "any":
        clauses.append(Item.currency == filters.currency)

    if filters.standalone_only:
        clauses.append(Item.is_standalone)  # noqa: E712

    if filters.date_from is not None:
        clauses.append(Topic.last_update_at >= filters.date_from)

    if filters.date_to is not None:
        clauses.append(Topic.last_update_at <= filters.date_to)

    return clauses


def build_order_clause(
    filters: SearchFilters,
    Item: type,
    Topic: type,
    distance_expr,
    matched_count_expr=None,
    agent_labels_arr=None,
) -> list:
    sort = filters.sort

    if sort == SortOrder.PRICE_ASC:
        return [Item.price.asc()]

    if sort == SortOrder.PRICE_DESC:
        return [Item.price.desc()]

    if sort == SortOrder.NEWEST:
        return [Topic.created_at.desc()]

    if sort == SortOrder.OLDEST:
        return [Topic.created_at.asc()]

    if sort == SortOrder.UPDATED:
        return [Topic.scraped_at.desc()]

    if sort == SortOrder.RELEVANCE:
        if agent_labels_arr is not None:
            return [
                func.cardinality(
                    func.array_intersection(Item.labels, agent_labels_arr)
                ).desc(),
                distance_expr.asc(),
            ]
        return [distance_expr.asc()]

    return [distance_expr.asc()]
