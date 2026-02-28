FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Dependencies — only invalidated if pyproject.toml or uv.lock change
COPY scraper/pyproject.toml scraper/uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Source code — invalidated on every code change, but deps are already installed
COPY shared/shared ./shared/
COPY scraper/scraper ./scraper/

# Install project itself (fast, no new packages to download)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["uvicorn", "scraper.main:app", "--host", "0.0.0.0", "--port", "8000"]
