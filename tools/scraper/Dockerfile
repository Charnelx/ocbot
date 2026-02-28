FROM python:3.13-slim

WORKDIR /app

RUN pip install uv

COPY tools/scraper/pyproject.toml .
RUN uv sync

COPY tools/scraper/ .

ENTRYPOINT ["uv", "run", "python"]
