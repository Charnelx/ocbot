import asyncio

import httpx
from langchain_core.tools import BaseTool

from search.config import settings
from search.logging import get_logger

logger = get_logger(__name__)


class WikipediaTool(BaseTool):
    name: str = "wikipedia_search"
    description: str = (  # noqa: E501
        "Search Wikipedia for computer hardware product or technology info. "
        "Use when you need to identify a product's generation, platform, socket "
        "type, or category. Input should be the product name, technology term "
        "or hardware family name."
        "Example #1: list of intel processors"
        "Example #2: geforce rtx 50 series"
        "Example #3: amd 700 chipset series"
    )

    def __init__(self) -> None:
        super().__init__()
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(settings.wikipedia_timeout_seconds),
            headers={
                "User-Agent": "OCBot-Search/0.1 (overclockers.ua hardware search)",
                "Accept": "application/json",
            },
        )

    def _run(self, query: str) -> str:
        return asyncio.run(self._arun(query))

    async def _arun(self, query: str) -> str:
        logger.debug("wikipedia_tool_called", query=query)

        try:
            title = await self._find_article_title(query)
            if not title:
                return ""

            extract = await self._get_article_intro(title)
            if not extract:
                return ""

            truncated = extract[: settings.wikipedia_max_chars]
            logger.debug(
                "wikipedia_tool_result",
                title=title,
                content=truncated,
                chars_returned=len(truncated),
            )
            return truncated

        except httpx.TimeoutException:
            logger.warning("wikipedia_tool_failed", error="timeout")
            return ""
        except Exception as exc:
            logger.warning("wikipedia_tool_failed", error=str(exc))
            return ""

    async def _find_article_title(self, query: str) -> str | None:
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "opensearch",
            "search": query,
            "limit": 1,
            "namespace": 0,
            "format": "json",
        }

        response = await self._client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        titles = data[1]
        return titles[0] if titles else None

    async def _get_article_intro(self, title: str) -> str | None:
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "titles": title,
            "prop": "extracts",
            "exintro": True,
            "explaintext": True,
            "format": "json",
        }

        response = await self._client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        pages = data.get("query", {}).get("pages", {})
        for page_data in pages.values():
            return page_data.get("extract")

        return None
