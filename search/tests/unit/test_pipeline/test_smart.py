from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from search.filters import SearchFilters, SortOrder


class TestSmartSearch:
    @pytest.mark.asyncio
    async def test_smart_search_returns_response(self):
        with (
            patch("search.pipeline.smart.classify_query") as mock_classify,
            patch("search.pipeline.smart.run_simple_search") as mock_simple,
        ):
            mock_classify.return_value = MagicMock(
                category="cpu",
                labels=["intel", "core-i7"],
                confidence=0.9,
            )

            mock_simple.return_value = MagicMock(
                total_matches=10,
                total_filtered=5,
                results=[],
            )

            from search.pipeline.smart import run_smart_search

            filters = SearchFilters(
                sort=SortOrder.RELEVANCE,
                score_auto_tune=True,
            )

            result = await run_smart_search(
                query="Intel Core i7",
                filters=filters,
            )

            assert result is not None

    @pytest.mark.asyncio
    async def test_smart_search_fallback_on_no_results(self):
        with (
            patch("search.pipeline.smart.classify_query") as mock_classify,
            patch("search.pipeline.smart.run_simple_search") as mock_simple,
        ):
            mock_classify.return_value = MagicMock(
                category="cpu",
                labels=["intel"],
                confidence=0.9,
            )

            mock_simple.return_value = MagicMock(
                total_matches=10,
                total_filtered=5,
                results=[],
            )

            from search.pipeline.smart import run_smart_search

            filters = SearchFilters(
                sort=SortOrder.RELEVANCE,
                score_auto_tune=True,
            )

            result = await run_smart_search(
                query="test",
                filters=filters,
            )

            assert result is not None

    @pytest.mark.asyncio
    async def test_smart_search_fallback_low_confidence(self):
        with (
            patch("search.pipeline.smart.classify_query") as mock_classify,
            patch("search.pipeline.smart.run_simple_search") as mock_simple,
        ):
            mock_classify.return_value = MagicMock(
                category=None,
                labels=[],
                confidence=0.3,
            )

            mock_simple.return_value = MagicMock(
                total_matches=10,
                total_filtered=5,
                results=[],
            )

            from search.pipeline.smart import run_smart_search

            filters = SearchFilters(
                sort=SortOrder.RELEVANCE,
            )

            result = await run_smart_search(
                query="test",
                filters=filters,
            )

            assert mock_simple.called


class TestDefaultMinScore:
    def test_default_min_score_value(self):
        from search.pipeline.smart import DEFAULT_MIN_SCORE

        assert DEFAULT_MIN_SCORE == 0.6
