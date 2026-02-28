import instructor
from instructor.core.exceptions import InstructorRetryException
from openai import AsyncOpenAI
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from enrichment.config import get_settings
from enrichment.extraction.prompt import SYSTEM_PROMPT, build_user_message
from enrichment.extraction.schemas import ExtractionResult
from enrichment.logging import get_logger

logger = get_logger(__name__)

settings = get_settings()

_raw_async_client = AsyncOpenAI(
    api_key=settings.openrouter_api_key.get_secret_value(),
    base_url=settings.openrouter_base_url,
)
_instructor_client = instructor.from_openai(_raw_async_client, mode=instructor.Mode.JSON)


def get_instructor_client():
    return _instructor_client


# ── Phase 2: LangChain AgentExecutor ─────────────────────────────────────
# Activate when ENRICHMENT_TOOLS is non-empty.
# Replace the instructor call in extract_items_from_topic() with this block.
#
# from langchain_openai import ChatOpenAI
# from langchain.agents import create_tool_calling_agent, AgentExecutor
# from langchain_core.prompts import ChatPromptTemplate
#
# _lc_llm = ChatOpenAI(
#     model=settings.llm_model,
#     openai_api_key=settings.openrouter_api_key.get_secret_value(),
#     openai_api_base=settings.openrouter_base_url,
#     max_tokens=settings.llm_max_tokens,
# )
# _lc_prompt = ChatPromptTemplate.from_messages([
#     ("system", SYSTEM_PROMPT),
#     ("human", "{input}"),
#     ("placeholder", "{agent_scratchpad}"),
# ])
# _agent = create_tool_calling_agent(_lc_llm, ENRICHMENT_TOOLS, _lc_prompt)
# _executor = AgentExecutor(agent=_agent, tools=ENRICHMENT_TOOLS, verbose=False)
#
# In extract_items_from_topic():
#   raw = await _executor.ainvoke({"input": user_message})
#   return ExtractionResult.model_validate_json(raw["output"])
# ─────────────────────────────────────────────────────────────────────────


@retry(
    stop=stop_after_attempt(settings.llm_max_attempts),
    wait=wait_exponential(min=settings.llm_retry_min_wait, max=settings.llm_retry_max_wait),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
async def extract_items_from_topic(
    topic_id: int,
    topic_title: str,
    clean_content: str,
) -> ExtractionResult:
    client = get_instructor_client()
    user_message = build_user_message(topic_title, clean_content)

    logger.debug(
        "llm_extraction_attempt",
        topic_id=topic_id,
        model=settings.llm_model,
        content_chars=len(clean_content),
    )

    try:
        result = await client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            response_model=ExtractionResult,
            max_tokens=settings.llm_max_tokens,
            max_retries=1,
        )

        logger.info(
            "llm_extraction_success",
            topic_id=topic_id,
            items_extracted=len(result.items),
        )

        return result

    except InstructorRetryException as exc:
        logger.warning(
            "llm_validation_failed",
            topic_id=topic_id,
            error=str(exc),
            exc_info=True,
        )
        raise
    except Exception as exc:
        logger.warning(
            "llm_call_failed",
            topic_id=topic_id,
            error=str(exc),
            error_type=type(exc).__name__,
            exc_info=True,
        )
        raise
