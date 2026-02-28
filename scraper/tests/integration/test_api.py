from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient


class TestScraperAPI:
    @pytest.fixture
    def mock_dependencies(self):
        mock_session = MagicMock()
        mock_session.execute = AsyncMock()
        mock_session.flush = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.add = MagicMock()

        mock_factory = MagicMock()
        mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_factory.return_value.__aexit__ = AsyncMock(return_value=None)

        mock_embedder = MagicMock()
        mock_embedder.embed.return_value = [[0.1] * 1024]

        mock_client = MagicMock()
        mock_client.fetch_forum_index = AsyncMock(return_value=["<html>Index</html>"])
        mock_client.fetch_topics_content = AsyncMock(return_value={"1": "<html>Topic</html>"})
        mock_client.close = AsyncMock()

        patches = [
            patch("scraper.main.async_session_factory", mock_factory),
            patch("scraper.main.TopicEmbedder", return_value=mock_embedder),
            patch("scraper.main.ForumClient", return_value=mock_client),
        ]

        for p in patches:
            p.start()

        yield {
            "session": mock_session,
            "factory": mock_factory,
            "embedder": mock_embedder,
            "client": mock_client,
        }

        for p in patches:
            p.stop()

    @pytest.fixture
    def client(self, mock_dependencies):
        import importlib

        import scraper.main

        importlib.reload(scraper.main)

        from scraper.main import app

        return TestClient(app)

    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_scrape_returns_202(self, client, mock_dependencies):
        response = client.post("/scrape", json={"page_count": 1})
        assert response.status_code == 202
        data = response.json()
        assert data["message"] == "Scraping started"
        assert data["page_count"] == 1

    def test_scrape_accepts_custom_params(self, client, mock_dependencies):
        response = client.post(
            "/scrape",
            json={
                "page_count": 10,
                "bulk_size": 5,
                "bulk_delay_ms": 1000,
                "user_agent": "Custom Agent",
            },
        )
        assert response.status_code == 202
        data = response.json()
        assert data["page_count"] == 10

    def test_scrape_uses_defaults(self, client, mock_dependencies):
        response = client.post("/scrape", json={})
        assert response.status_code == 202
        data = response.json()
        assert data["page_count"] == 5

    def test_scrape_response_model(self, client, mock_dependencies):
        response = client.post("/scrape", json={"page_count": 2})
        assert response.status_code == 202

        data = response.json()
        assert "message" in data
        assert "page_count" in data


class TestScrapeRequest:
    def test_scrape_request_defaults(self):
        from scraper.main import ScrapeRequest

        request = ScrapeRequest()
        assert request.page_count is None
        assert request.bulk_size is None
        assert request.bulk_delay_ms is None
        assert request.user_agent is None

    def test_scrape_request_with_values(self):
        from scraper.main import ScrapeRequest

        request = ScrapeRequest(
            page_count=10,
            bulk_size=5,
            bulk_delay_ms=1000,
            user_agent="Custom UA",
        )
        assert request.page_count == 10
        assert request.bulk_size == 5
        assert request.bulk_delay_ms == 1000
        assert request.user_agent == "Custom UA"


class TestScrapeResponse:
    def test_scrape_response_model(self):
        from scraper.main import ScrapeResponse

        response = ScrapeResponse(
            message="Test message",
            page_count=5,
        )
        assert response.message == "Test message"
        assert response.page_count == 5
