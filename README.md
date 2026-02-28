# OCBot - Overclockers.ua Used Electronics Discovery

Pilot system for aggregating, structuring, and searching used computer parts from the Overclockers.ua forum using LLM-powered extraction and hybrid search.

---

## Quick Start

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Start PostgreSQL and run migrations
docker compose up -d postgres
docker compose up --build migration

# 3. Start all services
docker compose up --build -d

# 4. Trigger first scrape (or use n8n at http://localhost:5678)
curl -X POST http://localhost:8000/scrape -H "Content-Type: application/json" \
  -d '{"page_count": 1}'
```

**Access the app at** http://localhost:3000

---

## Configuration

Copy `.env.example` to `.env` and configure:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection (auto-configured by docker-compose) |
| `ENRICHMENT_OPENROUTER_API_KEY` | **Required.** Get free key at openrouter.ai |
| `SEARCH_OPENROUTER_API_KEY` | Can share with enrichment |
| `N8N_USER` / `N8N_PASSWORD` | n8n admin credentials (default: admin/admin) |

All other variables have sensible defaults. See `.env.example` for full list.

---

## Services

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 3000 | Vue 3 web UI (via nginx) |
| Search API | 8002 | REST API for search |
| Scraper API | 8000 | Triggers scraping jobs |
| Enrichment API | 8001 | Background LLM processing |
| n8n | 5678 | Scheduler/orchestration |
| PostgreSQL | 5432 | Database + pgvector |

---

## How to Trigger Scraping

### Option A: Via n8n (recommended for automation)
1. Open http://localhost:5678
2. Login with `admin/admin`
3. Run the "scrape" workflow manually, or wait for scheduled trigger

### Option B: Direct API
```bash
curl -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{"page_count": 1}'
```

### Option C: Docker exec
```bash
docker compose exec scraper python -c "
import httpx
import asyncio
asyncio.run(httpx.AsyncClient().post(
    'http://localhost:8000/scrape',
    json={'page_count': 1}
))
"
```

---

## Common Commands

```bash
# Start services
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down

# Stop and delete data
docker compose down -v

# Run database migrations
docker compose up --build migration
```

---

## Testing

```bash
# Install dependencies (requires uv)
uv sync

# Run tests
pytest

# Lint
ruff check .
ruff format --check .
```

---

## Project Structure

```
OCBot/
├── docker-compose.yml     # Service orchestration
├── .env.example           # Environment template
├── shared/                # DB models, migrations, schemas
├── scraper/               # Fetches forum topics
├── enrichment/            # LLM item extraction
├── search/                # Hybrid search API
├── frontend/              # Vue 3 web UI
├── nginx/                 # Reverse proxy
└── n8n/                   # Workflow automation
```

---

## More Info

- [ARCHITECTURE.md](./Docs/ARCHITECTURE.md) — System design details
- [AGENTS.md](./AGENTS.md) — Development guidelines
