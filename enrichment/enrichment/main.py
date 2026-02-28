from contextlib import asynccontextmanager

from fastapi import FastAPI

from enrichment.config import get_settings
from enrichment.logging import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "enrichment_service_starting",
        model=settings.llm_model,
        default_limit=settings.enrich_default_limit,
        max_limit=settings.enrich_max_limit,
    )
    yield
    logger.info("enrichment_service_stopping")


app = FastAPI(
    title="Enrichment Service",
    description="LLM-powered extraction of structured product items from forum topics.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


def create_app() -> FastAPI:
    from enrichment.router import router

    app.include_router(router)
    return app


app = create_app()
