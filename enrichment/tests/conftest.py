from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from enrichment.extraction.schemas import (
    ExtractionResult,
    ExtractedItem,
    ItemCategory,
    ItemCurrency,
)


@pytest.fixture
def mock_db_session():
    session = MagicMock()
    session.execute = AsyncMock()
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def sample_topic():
    topic = MagicMock()
    topic.id = 1
    topic.external_id = "12345"
    topic.title = "Test Topic"
    topic.clean_content = "Test content"
    topic.enriched = False
    topic.enrichment_attempts = 0
    return topic


@pytest.fixture
def sample_extracted_items():
    return [
        ExtractedItem(
            title="Intel Core i7-12700K",
            raw_text_segment="Intel Core i7-12700K - 5000 UAH",
            category=ItemCategory.cpu,
            labels=["intel", "core-i7", "12th-gen"],
            price=5000.0,
            currency=ItemCurrency.UAH,
        ),
        ExtractedItem(
            title="ASUS ROG STRIX RTX 3080",
            raw_text_segment="ASUS ROG STRIX RTX 3080 - 15000 UAH",
            category=ItemCategory.gpu,
            labels=["asus", "rog-strix", "rtx-3080"],
            price=15000.0,
            currency=ItemCurrency.UAH,
        ),
    ]


@pytest.fixture
def sample_embeddings():
    return [[0.1] * 1024, [0.2] * 1024]


@pytest.fixture
def mock_instructor_client(mocker):
    mock = MagicMock()
    mock.chat.completions.create = AsyncMock()
    mocker.patch(
        "enrichment.extraction.agent.get_instructor_client",
        return_value=mock,
    )
    return mock
