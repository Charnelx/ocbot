import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from scraper.scraper.client import (
    ForumClient,
    TopicSummary,
    extract_topic_id_from_url,
)


class TestExtractTopicIdFromUrl:
    @pytest.mark.parametrize(
        "url,expected",
        [
            ("https://forum.overclockers.ua/topic/12345", "12345"),
            ("/topic/67890", "67890"),
            ("https://forum.overclockers.ua/f=26&t=111", "111"),
            ("https://forum.overclockers.ua/index.php?f=5&t=222", "222"),
            ("not_a_url", "not_a_url"),
            ("https://forum.overclockers.ua/topic/999", "999"),
            ("/f=10&t=555", "555"),
        ],
    )
    def test_extracts_topic_id(self, url, expected):
        assert extract_topic_id_from_url(url) == expected


class TestTopicSummary:
    def test_topic_summary_creation(self):
        topic = TopicSummary(
            external_id="123",
            title="Test Title",
            url="https://forum.overclockers.ua/topic/123",
            author="test_user",
        )
        assert topic.external_id == "123"
        assert topic.title == "Test Title"
        assert topic.author == "test_user"

    def test_topic_summary_with_optional_fields(self):
        topic = TopicSummary(
            external_id="123",
            title="Test",
            url="https://forum.overclockers.ua/topic/123",
            author="user",
            last_update_at="2024-01-15T10:30:00Z",
        )
        assert topic.last_update_at == "2024-01-15T10:30:00Z"


class TestForumClient:
    def test_build_headers(self):
        client = ForumClient(
            base_url="https://example.com",
            user_agent="Custom UA",
        )
        headers = client._build_headers()
        assert headers["User-Agent"] == "Custom UA"

    def test_client_initialization(self):
        client = ForumClient(
            base_url="https://forum.overclockers.ua",
            user_agent="Test",
            bulk_size=10,
            topics_per_page=20,
        )
        assert client.base_url == "https://forum.overclockers.ua"
        assert client.user_agent == "Test"
        assert client.bulk_size == 10
        assert client.topics_per_page == 20

    def test_semaphore_initialized(self):
        client = ForumClient(
            base_url="https://forum.overclockers.ua",
            user_agent="Test",
            bulk_size=5,
        )
        assert client.semaphore._value == 5


class TestForumClientAsync:
    """Async tests for ForumClient - requires session_factory injection."""

    @pytest.fixture
    def mock_session_class(self):
        class MockSession:
            def __init__(self, *args, **kwargs):
                self.get = AsyncMock()
                self.close = AsyncMock()

        return MockSession

    @pytest.fixture
    def mock_response(self):
        return MagicMock()

    @pytest.fixture
    def client(self, mock_session_class, mock_response):
        client = ForumClient(
            base_url="https://forum.overclockers.ua",
            user_agent="Test Agent",
            bulk_size=5,
            session_factory=mock_session_class,
        )
        client.client.get.return_value = mock_response
        return client

    @pytest.fixture
    def mock_session(self, client):
        return client.client

    @pytest.mark.asyncio
    async def test_fetch_page_returns_html(self, client, mock_response):
        mock_response.text = "<html>Test content</html>"
        mock_response.raise_for_status = MagicMock()

        result = await client.fetch_page("https://forum.overclockers.ua/topic/123")

        assert result == "<html>Test content</html>"
        client.client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_page_raises_on_error(self, client, mock_response):
        mock_response.raise_for_status = MagicMock(side_effect=Exception("HTTP 404"))

        with pytest.raises(Exception, match="HTTP 404"):
            await client.fetch_page("https://forum.overclockers.ua/topic/bad")

    @pytest.mark.asyncio
    async def test_fetch_page_passes_url_to_session(self, client, mock_response):
        mock_response.text = "<html></html>"
        mock_response.raise_for_status = MagicMock()

        await client.fetch_page("https://forum.overclockers.ua/topic/123")

        call_args = client.client.get.call_args
        assert call_args[0][0] == "https://forum.overclockers.ua/topic/123"

    @pytest.mark.asyncio
    async def test_close_closes_session(self, client, mock_session):
        await client.close()
        mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_page_uses_semaphore(self, client, mock_response):
        mock_response.text = "<html></html>"
        mock_response.raise_for_status = MagicMock()

        tasks = [client.fetch_page(f"https://forum.overclockers.ua/topic/{i}") for i in range(10)]
        await asyncio.gather(*tasks)

        assert client.client.get.call_count == 10

    @pytest.mark.asyncio
    async def test_fetch_forum_index_single_page(self, client, mock_response):
        mock_response.text = "<html>Page 1</html>"
        mock_response.raise_for_status = MagicMock()

        result = await client.fetch_forum_index(1)

        assert len(result) == 1
        assert result[0] == "<html>Page 1</html>"

    @pytest.mark.asyncio
    async def test_fetch_forum_index_multiple_pages(self, client, mock_response):
        mock_response.text = "<html>Page</html>"
        mock_response.raise_for_status = MagicMock()

        result = await client.fetch_forum_index(3)

        assert len(result) == 3

    @pytest.mark.asyncio
    async def test_fetch_topics_content_returns_dict(self, client, mock_response):
        mock_response.text = "<html>Topic content</html>"
        mock_response.raise_for_status = MagicMock()

        topics = [
            TopicSummary(external_id="1", title="Topic 1", url="https://forum.overclockers.ua/topic/1", author="user1"),
            TopicSummary(external_id="2", title="Topic 2", url="https://forum.overclockers.ua/topic/2", author="user2"),
        ]

        result = await client.fetch_topics_content(topics)

        assert isinstance(result, dict)
        assert len(result) == 2
        assert "1" in result
        assert "2" in result

    @pytest.mark.asyncio
    async def test_fetch_topics_content_handles_exception(self, client, mock_response):
        async def side_effect(*args, **kwargs):
            if "1" in str(args[0]):
                raise Exception("Network error")
            response = MagicMock()
            response.text = "<html>Content</html>"
            response.raise_for_status = MagicMock()
            return response

        client.client.get.side_effect = side_effect

        topics = [
            TopicSummary(external_id="1", title="Topic 1", url="https://forum.overclockers.ua/topic/1", author="user1"),
            TopicSummary(external_id="2", title="Topic 2", url="https://forum.overclockers.ua/topic/2", author="user2"),
        ]

        result = await client.fetch_topics_content(topics)

        assert len(result) == 1
        assert "2" in result
