from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession


class MockTopic:
    """Mock topic object to avoid MagicMock attribute issues."""

    def __init__(
        self,
        external_id: str,
        content_hash: str,
        title: str = "",
        raw_content: str = "",
        clean_content: str = "",
        author: str = "",
        last_update_at: datetime | None = None,
        scraped_at: datetime | None = None,
        enriched: bool = False,
        embedding: list | None = None,
    ):
        self.external_id = external_id
        self.content_hash = content_hash
        self.title = title
        self.raw_content = raw_content
        self.clean_content = clean_content
        self.author = author
        self.last_update_at = last_update_at
        self.scraped_at = scraped_at
        self.enriched = enriched
        self.embedding = embedding


class TestTopicRepository:
    @pytest.fixture
    def mock_topic_model(self):
        with patch("scraper.repository.Topic") as mock:
            yield mock

    @pytest.fixture
    def mock_session(self):
        session = AsyncMock(spec=AsyncSession)
        return session

    @pytest.fixture
    def repository(self, mock_session):
        from scraper.repository import TopicRepository

        return TopicRepository(session=mock_session)

    @pytest.mark.asyncio
    async def test_get_by_external_id_returns_topic(self, repository, mock_session):
        # simulates a Topic ORM instance
        expected = MagicMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = expected
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_external_id("123")

        assert result is expected
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_external_id_returns_none(self, repository, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.get_by_external_id("nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_content_hash_returns_hash(self, repository, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = "abc123"
        mock_session.execute.return_value = mock_result

        result = await repository.get_content_hash("123")

        assert result == "abc123"

    @pytest.mark.asyncio
    async def test_get_content_hash_returns_none(self, repository, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await repository.get_content_hash("nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_upsert_creates_new_topic(self, repository, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result, created = await repository.upsert_topic(
            external_id="123",
            title="Test",
            raw_content="raw",
            clean_content="clean",
            content_hash="hash",
            author="user",
            last_update_at=datetime.now(),
            embedding=[0.1] * 1024,
        )

        assert created is True
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_upsert_skips_unchanged_content(self, repository, mock_session):
        existing = MockTopic(external_id="123", content_hash="same_hash")

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing
        mock_session.execute.return_value = mock_result

        result, created = await repository.upsert_topic(
            external_id="123",
            title="Test",
            raw_content="raw",
            clean_content="clean",
            content_hash="same_hash",
            author="user",
            last_update_at=datetime.now(),
            embedding=None,
        )

        assert created is False
        mock_session.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_upsert_updates_existing_topic(self, repository, mock_session):
        existing = MockTopic(external_id="123", content_hash="old_hash")

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing
        mock_session.execute.return_value = mock_result

        result, created = await repository.upsert_topic(
            external_id="123",
            title="Updated Title",
            raw_content="new raw",
            clean_content="new clean",
            content_hash="new_hash",
            author="new_user",
            last_update_at=datetime.now(),
            embedding=[0.2] * 1024,
        )

        assert created is True
        assert existing.title == "Updated Title"
        assert existing.content_hash == "new_hash"
        assert existing.enriched is False

    @pytest.mark.asyncio
    async def test_upsert_resets_enriched_flag_on_update(self, repository, mock_session):
        existing = MockTopic(external_id="123", content_hash="old_hash", enriched=True)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing
        mock_session.execute.return_value = mock_result

        await repository.upsert_topic(
            external_id="123",
            title="Test",
            raw_content="raw",
            clean_content="clean",
            content_hash="new_hash",
            author="user",
            last_update_at=datetime.now(),
            embedding=None,
        )

        assert existing.enriched is False

    @pytest.mark.asyncio
    async def test_commit_calls_session_commit(self, repository, mock_session):
        await repository.commit()
        mock_session.commit.assert_called_once()
