FROM python:3.13-slim

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

RUN pip install uv

COPY search/pyproject.toml search/uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

COPY shared/shared ./shared/

COPY search/search/ ./search/
COPY search/tests/ ./tests/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"

CMD ["uv", "run", "uvicorn", "search.main:app", "--host", "0.0.0.0", "--port", "8002"]
