from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import delete, select, update

from enrichment.extraction.schemas import (
    ExtractionResult,
    ExtractedItem,
    ItemCategory,
    ItemCurrency,
)
from enrichment import repository


class TestFetchUnenrichedTopics:
    @pytest.mark.asyncio
    async def test_fetch_unenriched_topics_query(self):
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute = AsyncMock(return_value=mock_result)

        @asynccontextmanager
        async def mock_session_factory():
            yield mock_session

        with patch.object(repository, "async_session_factory", mock_session_factory):
            topics = await repository.fetch_unenriched_topics(limit=10)

            mock_session.execute.assert_called_once()
            call_args = mock_session.execute.call_args[0][0]
            assert "SELECT" in str(call_args)
            assert "enriched" in str(call_args).lower()


class TestReplaceTopicItems:
    @pytest.mark.asyncio
    async def test_replace_topic_items_deletes_old_first(self):
        mock_session = MagicMock()
        mock_session.execute = AsyncMock()
        mock_session.commit = AsyncMock()

        mock_topic = MagicMock()
        mock_topic.id = 1

        extracted_items = [
            ExtractedItem(
                title="Intel Core i7-12700K",
                raw_text_segment="Test",
                category=ItemCategory.cpu,
                labels=["intel"],
                price=5000.0,
                currency=ItemCurrency.UAH,
            ),
        ]
        embeddings = [[0.1] * 1024]

        @asynccontextmanager
        async def mock_session_factory():
            yield mock_session

        with patch.object(repository, "async_session_factory", mock_session_factory):
            await repository.replace_topic_items(mock_topic, extracted_items, embeddings, True)

            delete_call = mock_session.execute.call_args_list[0][0][0]
            assert "DELETE" in str(delete_call)
            mock_session.commit.assert_called_once()


class TestMarkTopicEnrichedEmpty:
    @pytest.mark.asyncio
    async def test_mark_topic_enriched_empty(self):
        mock_session = MagicMock()
        mock_session.execute = AsyncMock()
        mock_session.commit = AsyncMock()

        mock_topic = MagicMock()
        mock_topic.id = 1

        @asynccontextmanager
        async def mock_session_factory():
            yield mock_session

        with patch.object(repository, "async_session_factory", mock_session_factory):
            await repository.mark_topic_enriched_empty(mock_topic)

            assert mock_session.execute.call_count == 2
            mock_session.commit.assert_called_once()


class TestMarkTopicFailed:
    @pytest.mark.asyncio
    async def test_mark_topic_failed_increments_attempts(self):
        mock_session = MagicMock()
        mock_session.execute = AsyncMock()
        mock_session.commit = AsyncMock()

        mock_topic = MagicMock()
        mock_topic.id = 1
        mock_topic.title = "Test Topic"

        @asynccontextmanager
        async def mock_session_factory():
            yield mock_session

        with patch.object(repository, "async_session_factory", mock_session_factory):
            await repository.mark_topic_failed(mock_topic, "Test error")

            mock_session.execute.assert_called_once()
            mock_session.commit.assert_called_once()

            call_args = mock_session.execute.call_args[0][0]
            assert "UPDATE" in str(call_args)

    @pytest.mark.asyncio
    async def test_mark_topic_failed_truncates_error(self):
        mock_session = MagicMock()
        mock_session.execute = AsyncMock()
        mock_session.commit = AsyncMock()

        mock_topic = MagicMock()
        mock_topic.id = 1
        mock_topic.title = "Test Topic"

        long_error = "a" * 2000

        @asynccontextmanager
        async def mock_session_factory():
            yield mock_session

        with patch.object(repository, "async_session_factory", mock_session_factory):
            await repository.mark_topic_failed(mock_topic, long_error)

            mock_session.execute.assert_called_once()
            mock_session.commit.assert_called_once()
