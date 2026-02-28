from typing import Protocol

from langchain_core.tools import BaseTool

from search.pipeline.tools.wikipedia import WikipediaTool


class SearchTool(Protocol):
    name: str
    description: str

    async def _arun(self, query: str) -> str: ...


SEARCH_TOOLS: list[BaseTool] = [
    WikipediaTool(),
]
