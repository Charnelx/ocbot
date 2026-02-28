from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from pydantic import ValidationError

from enrichment.extraction.agent import extract_items_from_topic
from enrichment.extraction.schemas import (
    ExtractionResult,
    ExtractedItem,
    ItemCategory,
    ItemCurrency,
)


class TestExtractItemsFromTopic:
    @pytest.fixture
    def mock_extraction_result(self):
        item = ExtractedItem(
            title="Intel Core i7-12700K",
            raw_text_segment="Intel Core i7-12700K - 5000 UAH",
            category=ItemCategory.cpu,
            labels=["intel", "core-i7"],
            price=5000.0,
            currency=ItemCurrency.UAH,
        )
        return ExtractionResult(items=[item])

    @pytest.mark.asyncio
    async def test_extract_items_success(self, mock_extraction_result):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content='{"items": []}'))]
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        with patch(
            "enrichment.extraction.agent.get_instructor_client",
            return_value=mock_client,
        ):
            result = await extract_items_from_topic(
                topic_id=1,
                topic_title="Test Topic",
                clean_content="Test content",
            )
            assert result is not None

    @pytest.mark.asyncio
    async def test_extract_items_raises_on_error(self):
        mock_client = MagicMock()
        mock_client.chat.completions.create = AsyncMock(side_effect=Exception("LLM error"))

        with patch(
            "enrichment.extraction.agent.get_instructor_client",
            return_value=mock_client,
        ):
            with pytest.raises(Exception):
                await extract_items_from_topic(
                    topic_id=1,
                    topic_title="Test Topic",
                    clean_content="Test content",
                )

    @pytest.mark.asyncio
    async def test_extract_items_validates_response(self):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="not valid json"))]

        async def mock_create(*args, **kwargs):
            return mock_response

        mock_client.chat.completions.create = mock_create

        with patch(
            "enrichment.extraction.agent.get_instructor_client",
            return_value=mock_client,
        ):
            result = await extract_items_from_topic(
                topic_id=1,
                topic_title="Test Topic",
                clean_content="Test content",
            )
            assert result is not None
            assert len(result.items) == 0


class TestGetInstructorClient:
    def test_get_instructor_client_returns_client(self):
        from enrichment.extraction.agent import get_instructor_client

        client = get_instructor_client()
        assert client is not None
