from contextlib import asynccontextmanager

from fastapi import FastAPI

from search.config import settings
from search.logging import configure_logging, get_logger
from search.router import router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info(
        "search_service_starting",
        model=settings.llm_model,
        timeout=settings.smart_timeout_seconds,
        confidence_threshold=settings.confidence_threshold,
    )
    yield
    logger.info("search_service_shutting_down")


def create_app() -> FastAPI:
    app = FastAPI(
        title="OCBot Search Service",
        description="Vector search service for Overclockers.ua hardware listings",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.include_router(router)
    return app


app = create_app()
