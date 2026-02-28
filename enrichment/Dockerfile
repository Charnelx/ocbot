FROM python:3.13-slim

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

RUN pip install uv

COPY enrichment/pyproject.toml enrichment/uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

COPY shared/shared ./shared/

COPY enrichment/enrichment ./enrichment/
COPY enrichment/tests ./tests/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install pytest pytest-asyncio pytest-mock

ENV PATH="/app/.venv/bin:$PATH"

CMD ["uv", "run", "uvicorn", "enrichment.main:app", "--host", "0.0.0.0", "--port", "8001"]
