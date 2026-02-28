import instructor
from langchain.agents import create_agent
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from openai import AsyncOpenAI

from search.config import settings
from search.logging import get_logger
from search.pipeline.prompt import (
    AGENT_SYSTEM_PROMPT,
    EXTRACTION_SYSTEM_PROMPT,
    build_agent_user_message,
    build_extraction_user_message,
)
from search.pipeline.schemas import AgentClassification
from search.pipeline.tools import SEARCH_TOOLS

logger = get_logger(__name__)

_chat_llm: ChatOpenAI | None = None
_instructor_client: instructor.Instructor | None = None
_agent: Runnable | None = None


def _get_chat_llm() -> ChatOpenAI:
    global _chat_llm
    if _chat_llm is None:
        _chat_llm = ChatOpenAI(
            model=settings.llm_model,
            openai_api_key=settings.openrouter_api_key,
            openai_api_base=settings.openrouter_base_url,
            max_tokens=settings.llm_max_tokens,
        )
    return _chat_llm


def _get_instructor_client() -> instructor.Instructor:
    global _instructor_client
    if _instructor_client is None:
        _raw_client = AsyncOpenAI(
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
        )
        _instructor_client = instructor.from_openai(
            _raw_client, mode=instructor.Mode.JSON
        )
    return _instructor_client


def _get_agent() -> Runnable:
    global _agent
    if _agent is None:
        _agent = create_agent(
            model=_get_chat_llm(),
            tools=[], # tools removed
            system_prompt=AGENT_SYSTEM_PROMPT,
        )
    return _agent


async def classify_query(query: str) -> AgentClassification:
    logger.debug("smart_agent_call1_start", query_len=len(query))

    agent = _get_agent()
    input_message = build_agent_user_message(query)
    raw_output = await agent.ainvoke(
        {"messages": [{"role": "user", "content": input_message}]}
    )
    messages = raw_output.get("messages", [])
    agent_text = messages[-1].content if messages else ""

    logger.debug(
        "smart_agent_call1_complete",
        output_len=len(agent_text),
    )

    logger.debug("smart_agent_call2_start", input_len=len(agent_text))

    user_message = build_extraction_user_message(query, agent_text)
    client = _get_instructor_client()

    classification = await client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        response_model=AgentClassification,
        max_tokens=settings.llm_max_tokens,
        max_retries=1,
    )

    logger.info(
        "smart_agent_classification",
        category=classification.category.value,
        labels_count=len(classification.labels),
        labels=classification.labels,
        confidence=classification.confidence,
        reasoning=classification.reasoning,
    )

    return classification
