from datetime import datetime
from unittest.mock import MagicMock

import pytest

from search.filters import (
    SearchFilters,
    SortOrder,
    build_filter_clauses,
    build_order_clause,
    from_query_params,
)


class TestSearchFilters:
    def test_search_filters_limit_bounds(self):
        filters = SearchFilters(limit=200)
        assert filters.limit == 100

    def test_search_filters_limit_zero(self):
        filters = SearchFilters(limit=0)
        assert filters.limit == 1

    def test_search_filters_limit_negative(self):
        filters = SearchFilters(limit=-5)
        assert filters.limit == 1

    def test_search_filters_offset_negative(self):
        filters = SearchFilters(offset=-10)
        assert filters.offset == 0


class TestFromQueryParams:
    def test_from_query_params_default(self):
        filters = from_query_params()
        assert filters.sort == SortOrder.RELEVANCE
        assert filters.offset == 0

    def test_from_query_params_with_values(self):
        filters = from_query_params(
            categories=["cpu", "gpu"],
            price_min=100,
            price_max=5000,
            currency="UAH",
            standalone_only=True,
            sort=SortOrder.PRICE_ASC,
            limit=50,
            offset=10,
        )
        assert filters.categories == ["cpu", "gpu"]
        assert filters.price_min == 100
        assert filters.price_max == 5000
        assert filters.currency == "UAH"
        assert filters.standalone_only is True
        assert filters.sort == SortOrder.PRICE_ASC
        assert filters.limit == 50
        assert filters.offset == 10


class MockItem:
    category = "cpu"
    price = 1000
    currency = "UAH"
    is_standalone = True
    labels = ["intel", "core-i7"]


class MockTopic:
    last_update_at = datetime(2024, 1, 1)
    created_at = datetime(2024, 1, 1)
    scraped_at = datetime(2024, 1, 1)


class TestBuildFilterClauses:
    def test_build_filter_clauses_categories(self):
        filters = SearchFilters(categories=["cpu", "gpu"])
        clauses = build_filter_clauses(filters, MockItem, MockTopic)
        assert len(clauses) == 1

    def test_build_filter_clauses_price_range(self):
        filters = SearchFilters(price_min=100, price_max=5000)
        clauses = build_filter_clauses(filters, MockItem, MockTopic)
        assert len(clauses) == 2

    def test_build_filter_clauses_currency(self):
        filters = SearchFilters(currency="UAH")
        clauses = build_filter_clauses(filters, MockItem, MockTopic)
        assert len(clauses) == 1

    def test_build_filter_clauses_currency_any(self):
        filters = SearchFilters(currency="any")
        clauses = build_filter_clauses(filters, MockItem, MockTopic)
        assert len(clauses) == 0

    def test_build_filter_clauses_standalone_only(self):
        filters = SearchFilters(standalone_only=True)
        clauses = build_filter_clauses(filters, MockItem, MockTopic)
        assert len(clauses) == 1

    def test_build_filter_clauses_date_range(self):
        filters = SearchFilters(
            date_from=datetime(2024, 1, 1),
            date_to=datetime(2024, 12, 31),
        )
        clauses = build_filter_clauses(filters, MockItem, MockTopic)
        assert len(clauses) == 2


class TestBuildOrderClause:
    def test_build_order_clause_price_asc(self):
        filters = SearchFilters(sort=SortOrder.PRICE_ASC)
        distance_expr = MagicMock()
        order = build_order_clause(filters, MockItem, MockTopic, distance_expr)
        assert "asc" in str(order).lower()

    def test_build_order_clause_price_desc(self):
        filters = SearchFilters(sort=SortOrder.PRICE_DESC)
        distance_expr = MagicMock()
        order = build_order_clause(filters, MockItem, MockTopic, distance_expr)
        assert "desc" in str(order).lower()

    def test_build_order_clause_newest(self):
        filters = SearchFilters(sort=SortOrder.NEWEST)
        distance_expr = MagicMock()
        order = build_order_clause(filters, MockItem, MockTopic, distance_expr)
        assert "created_at" in str(order).lower()
        assert "desc" in str(order).lower()

    def test_build_order_clause_oldest(self):
        filters = SearchFilters(sort=SortOrder.OLDEST)
        distance_expr = MagicMock()
        order = build_order_clause(filters, MockItem, MockTopic, distance_expr)
        assert "created_at" in str(order).lower()
        assert "asc" in str(order).lower()

    def test_build_order_clause_updated(self):
        filters = SearchFilters(sort=SortOrder.UPDATED)
        distance_expr = MagicMock()
        order = build_order_clause(filters, MockItem, MockTopic, distance_expr)
        assert "scraped_at" in str(order).lower()

    def test_build_order_clause_relevance(self):
        filters = SearchFilters(sort=SortOrder.RELEVANCE)
        distance_expr = MagicMock()
        order = build_order_clause(filters, MockItem, MockTopic, distance_expr)
        assert order is not None

    def test_build_order_clause_relevance_with_labels(self):
        filters = SearchFilters(sort=SortOrder.RELEVANCE)
        distance_expr = MagicMock()
        agent_labels = ["intel", "core-i7"]
        order = build_order_clause(
            filters, MockItem, MockTopic, distance_expr, agent_labels_arr=agent_labels
        )
        assert order is not None
