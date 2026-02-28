from datetime import datetime
from unittest.mock import MagicMock

import pytest

from scraper.exceptions import EmbeddingError
from scraper.service import ScrapingResult, ScrapingService
from scraper.scraper.client import TopicSummary


class TestScrapingServiceInit:
    """Tests for ScrapingService initialization."""

    def test_initializes_with_dependencies(self):
        """Test service initializes with client, embedder, and repository."""
        mock_client = MagicMock()
        mock_embedder = MagicMock()
        mock_repository = MagicMock()

        service = ScrapingService(
            client=mock_client,
            embedder=mock_embedder,
            repository=mock_repository,
        )

        assert service.client is mock_client
        assert service.embedder is mock_embedder
        assert service.repository is mock_repository


class TestScrapingResult:
    """Tests for ScrapingResult dataclass."""

    def test_creates_result(self):
        """Test ScrapingResult can be created with required fields."""
        result = ScrapingResult(
            processed_count=10,
            skipped_count=2,
            total_duration_sec=5.5,
        )

        assert result.processed_count == 10
        assert result.skipped_count == 2
        assert result.total_duration_sec == 5.5


class TestParseDatetime:
    """Tests for _parse_datetime helper method."""

    @pytest.fixture
    def service(self):
        mock_client = MagicMock()
        mock_embedder = MagicMock()
        mock_repository = MagicMock()
        return ScrapingService(
            client=mock_client,
            embedder=mock_embedder,
            repository=mock_repository,
        )

    def test_parses_iso_format_with_z(self, service):
        """Test parsing ISO format with Z suffix."""
        result = service._parse_datetime("2024-01-15T10:30:00Z")

        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_parses_iso_format_with_offset(self, service):
        """Test parsing ISO format with +00:00 offset."""
        result = service._parse_datetime("2024-01-15T10:30:00+00:00")

        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_returns_utcnow_for_none(self, service):
        """Test returns utcnow for None input."""
        result = service._parse_datetime(None)

        assert isinstance(result, datetime)

    def test_returns_utcnow_for_invalid_format(self, service):
        """Test returns utcnow for invalid date string."""
        result = service._parse_datetime("not-a-date")

        assert isinstance(result, datetime)


class TestProcessContents:
    """Tests for _process_contents method."""

    @pytest.fixture
    def service(self):
        mock_client = MagicMock()
        mock_embedder = MagicMock()
        mock_repository = MagicMock()
        return ScrapingService(
            client=mock_client,
            embedder=mock_embedder,
            repository=mock_repository,
        )

    @pytest.fixture
    def sample_topics(self):
        return [
            TopicSummary(
                external_id="1",
                title="Test Topic 1",
                url="https://forum.overclockers.ua/topic/1",
                author="user1",
                last_update_at="2024-01-15T10:30:00Z",
            ),
            TopicSummary(
                external_id="2",
                title="Test Topic 2",
                url="https://forum.overclockers.ua/topic/2",
                author="user2",
                last_update_at=None,
            ),
        ]

    def test_processes_valid_topics(self, service, sample_topics):
        """Test processing topics with content."""
        contents = {
            "1": "<html><div class='post'><div class='content'>Content 1</div></div></html>",
            "2": "<html><div class='post'><div class='content'>Content 2</div></div></html>",
        }

        result = service._process_contents(sample_topics, contents)

        assert len(result) == 2
        assert result[0]["external_id"] == "1"
        assert result[0]["title"] == "Test Topic 1"
        assert result[0]["clean_content"] == "Content 1"
        assert result[0]["content_hash"] is not None
        assert result[1]["external_id"] == "2"

    def test_skips_topics_without_content(self, service, sample_topics):
        """Test skips topics that have no content."""
        contents = {"1": "<html>Content</html>"}

        result = service._process_contents(sample_topics, contents)

        assert len(result) == 1
        assert result[0]["external_id"] == "1"


class TestGenerateEmbeddings:
    """Tests for _generate_embeddings method."""

    @pytest.fixture
    def service(self):
        mock_client = MagicMock()
        mock_embedder = MagicMock()
        mock_repository = MagicMock()
        return ScrapingService(
            client=mock_client,
            embedder=mock_embedder,
            repository=mock_repository,
        )

    def test_generates_embeddings(self, service):
        """Test generates embeddings for topics."""
        service.embedder.embed.return_value = [[0.1] * 1024, [0.2] * 1024]

        topics = [
            {"clean_content": "Text 1"},
            {"clean_content": "Text 2"},
        ]

        result = service._generate_embeddings(topics)

        assert len(result) == 2
        service.embedder.embed.assert_called_once()

    def test_returns_empty_list_for_empty_topics(self, service):
        """Test returns empty list when no topics."""
        result = service._generate_embeddings([])

        assert result == []
        service.embedder.embed.assert_not_called()

    def test_raises_embedding_error_on_exception(self, service):
        """Test raises EmbeddingError when embedder fails."""
        service.embedder.embed.side_effect = Exception("Model failed")

        topics = [{"clean_content": "Text"}]

        with pytest.raises(EmbeddingError):
            service._generate_embeddings(topics)
