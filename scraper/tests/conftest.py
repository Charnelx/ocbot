from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def mock_db_session():
    session = MagicMock()
    session.execute = AsyncMock()
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def sample_topic_data():
    return {
        "external_id": "12345",
        "title": "Test Topic Title",
        "raw_content": "<div class='content'>Raw HTML content</div>",
        "clean_content": "Clean text content",
        "content_hash": "abc123def456",
        "author": "test_user",
        "last_update_at": "2024-01-15T10:30:00",
    }


@pytest.fixture
def fixtures_dir():
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def forum_index_html(fixtures_dir):
    return (fixtures_dir / "forum_index.html").read_text()


@pytest.fixture
def topic_page_html(fixtures_dir):
    return (fixtures_dir / "topic_page.html").read_text()


@pytest.fixture
def mock_sentence_transformer():
    mock = MagicMock()
    mock.encode.return_value = [[0.1] * 1024]
    return mock


@pytest.fixture
def mock_curl_response():
    response = MagicMock()
    response.text = "<html>Mock HTML</html>"
    response.raise_for_status = MagicMock()
    return response
