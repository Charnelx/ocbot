import asyncio
import logging
import re
from dataclasses import dataclass
from typing import Any

from curl_cffi.requests import AsyncSession

logger = logging.getLogger(__name__)


@dataclass
class TopicSummary:
    external_id: str
    title: str
    url: str
    author: str
    last_update_at: str | None = None
    created_at: str | None = None
    is_closed: bool = False


class ForumClient:
    def __init__(
        self,
        base_url: str,
        user_agent: str,
        bulk_size: int = 10,
        topics_per_page: int = 40,
        session_factory: type | None = None,
    ):
        self.base_url = base_url
        self.user_agent = user_agent
        self.bulk_size = bulk_size
        self.topics_per_page = topics_per_page
        self.semaphore = asyncio.Semaphore(bulk_size)

        factory = session_factory or AsyncSession
        self.client = factory(
            timeout=30,
            impersonate="chrome120",
            allow_redirects=True,
        )

    def _build_headers(self) -> dict[str, str]:
        return {"User-Agent": self.user_agent}

    async def close(self) -> None:
        await self.client.close()

    async def fetch_page(self, url: str) -> str:
        async with self.semaphore:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.text

    async def fetch_forum_index(self, page_count: int) -> list[str]:
        html_pages: list[str] = []

        for page in range(1, page_count + 1):
            if page == 1:
                url = self.base_url
            else:
                start = (page - 1) * self.topics_per_page
                url = f"{self.base_url}&start={start}"

            logger.debug("Fetching forum index page", extra={"page": page, "url": url})
            html = await self.fetch_page(url)
            html_pages.append(html)

        return html_pages

    async def fetch_topics_content(self, topics: list[TopicSummary]) -> dict[str, str]:
        topic_contents: dict[str, str] = {}

        async def fetch_single(topic: TopicSummary) -> tuple[str, str]:
            html = await self.fetch_page(topic.url)
            return topic.external_id, html

        tasks = [fetch_single(t) for t in topics]
        results: list[Any] = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                logger.warning("Failed to fetch topic", exc_info=True)
                continue
            ext_id, html = result
            topic_contents[ext_id] = html

        return topic_contents


def extract_topic_id_from_url(url: str) -> str:
    match = re.search(r"/topic/(\d+)", url)
    if match:
        return match.group(1).split("&")[0]
    match = re.search(r"f=(\d+).*t=(\d+)", url)
    if match:
        return match.group(2).split("&")[0]
    return url.split("&")[0]
