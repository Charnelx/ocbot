from typing import Annotated

import httpx
from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from pydantic import BaseModel

from enrichment import pipeline
from enrichment.config import get_settings
from enrichment.logging import get_logger

logger = get_logger(__name__)

settings = get_settings()

router = APIRouter()


class HealthResponse(BaseModel):
    status: str


class ReadyResponse(BaseModel):
    status: str


class EnrichResponse(BaseModel):
    message: str
    limit: int


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(status="healthy")


@router.get("/ready", response_model=ReadyResponse)
async def readiness_check() -> ReadyResponse:
    if pipeline.is_busy():
        raise HTTPException(status_code=503, detail={"status": "busy"})
    return ReadyResponse(status="idle")


async def _call_webhook(webhook_url: str | None, payload: dict) -> None:
    """Call a webhook URL with the given payload."""
    if not webhook_url:
        return

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.post(webhook_url, json=payload)
        logger.info("Webhook called", extra={"webhook_url": webhook_url, "status": payload.get("status")})
    except Exception as e:
        logger.warning("Webhook call failed", extra={"webhook_url": webhook_url, "error": str(e)})


@router.post("/enrich", response_model=EnrichResponse, status_code=202)
async def trigger_enrichment(
    background_tasks: BackgroundTasks,
    limit: Annotated[int | None, Query(ge=1)] = None,
    webhook_url: Annotated[str | None, Query()] = None,
) -> EnrichResponse:
    if pipeline.is_busy():
        raise HTTPException(status_code=409, detail="An enrichment run is already in progress.")

    effective_limit = min(limit or settings.enrich_default_limit, settings.enrich_max_limit)
    effective_webhook = webhook_url or settings.webhook_url

    logger.info("enrich_triggered", limit=effective_limit)

    background_tasks.add_task(_run_and_log, effective_limit, effective_webhook)

    return EnrichResponse(message="Enrichment started", limit=effective_limit)


async def _run_and_log(limit: int, webhook_url: str) -> None:
    try:
        result = await pipeline.run_enrichment(limit)
        logger.info(
            "enrich_run_complete",
            requested=result.requested,
            processed=result.processed,
            succeeded=result.succeeded,
            failed=result.failed,
            skipped_empty=result.skipped_empty,
        )

        await _call_webhook(
            webhook_url,
            {
                "status": "success",
                "service": "enrichment",
                "requested": result.requested,
                "processed": result.processed,
                "succeeded": result.succeeded,
                "failed": result.failed,
                "skipped_empty": result.skipped_empty,
                "error": None,
            },
        )
    except RuntimeError as exc:
        logger.warning("enrich_run_skipped", error=str(exc))
        await _call_webhook(
            webhook_url,
            {
                "status": "error",
                "service": "enrichment",
                "requested": limit,
                "processed": 0,
                "succeeded": 0,
                "failed": 0,
                "skipped_empty": 0,
                "error": str(exc),
            },
        )
    except Exception as exc:
        logger.error("enrich_run_error", error=str(exc), error_type=type(exc).__name__)
        await _call_webhook(
            webhook_url,
            {
                "status": "error",
                "service": "enrichment",
                "requested": limit,
                "processed": 0,
                "succeeded": 0,
                "failed": 0,
                "skipped_empty": 0,
                "error": str(exc),
            },
        )
