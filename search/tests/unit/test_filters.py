from datetime import datetime

import pytest

from search.filters import (
    SearchFilters,
    SortOrder,
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


class TestSortOrder:
    def test_sort_order_values(self):
        assert SortOrder.RELEVANCE.value == "relevance"
        assert SortOrder.PRICE_ASC.value == "price_asc"
        assert SortOrder.PRICE_DESC.value == "price_desc"
        assert SortOrder.NEWEST.value == "newest"
        assert SortOrder.OLDEST.value == "oldest"
        assert SortOrder.UPDATED.value == "updated"

    def test_sort_order_all_values(self):
        values = [s.value for s in SortOrder]
        assert "relevance" in values
        assert "price_asc" in values
        assert "price_desc" in values
        assert "newest" in values
        assert "oldest" in values
        assert "updated" in values


class TestSearchFiltersDefaultValues:
    def test_defaults(self):
        filters = SearchFilters()
        assert filters.categories is None
        assert filters.price_min is None
        assert filters.price_max is None
        assert filters.currency is None
        assert filters.standalone_only is False
        assert filters.date_from is None
        assert filters.date_to is None
        assert filters.sort == SortOrder.RELEVANCE
        assert filters.limit is None
        assert filters.offset == 0
        assert filters.min_score is None
        assert filters.score_auto_tune is False
