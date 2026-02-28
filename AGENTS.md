# AGENTS.md

This file defines the rules and conventions that all AI agents must follow when working in this codebase. Rules are mandatory unless explicitly overridden by the user in a given session.

---

## Project Architecture

**Before starting any task, read `ARCHITECTURE.md`** located in `./Docs` folder.

`ARCHITECTURE.md` is the source of truth for the project's goals, architecture, structure, requirements, stack, and dependencies. You must:
- Read it at the start of every new session for context reference.
- Follow it strictly — do not introduce patterns, dependencies, or structural decisions that conflict with it.
- **Keep it up to date.** Whenever a change affects the project structure, adds a dependency, modifies a service boundary, or changes a significant design decision, update `ARCHITECTURE.md` as part of that same task. Do not leave it stale.

---

## Workflow

### Break Down Tasks
Never attempt a large task in one pass. Before writing any code:
1. Decompose the task into small, self-contained steps.
2. Present the plan to the user if the scope is non-trivial.
3. Implement one step at a time, test it, confirm it works, then move to the next.

### Documentation Lookup
When you need to search documentation for libraries, frameworks, or APIs, use `context7` tools (context7_resolve-library-id and context7_query-docs). This ensures you have accurate, up-to-date information rather than relying on potentially outdated knowledge.
Check pyproject.toml or requirements.txt before using `context7` to ensure there's no versions missmatch between libraries you're using and documentation you're reading.  

### Task Completion & Handoff
When the current task is fully done — code written, tests passing, linter clean, `ARCHITECTURE.md` updated if needed — explicitly signal completion with a short summary of what was done and what the user should review before committing. Do not silently stop.

The completion message must always include a **"How to run / verify"** section with exact, copy-pasteable commands the user needs to test, run, or validate the changes. Assume nothing is already running. Cover: installing dependencies, running migrations if applicable, starting services, running the test suite, and any manual verification steps specific to the feature. Example:

> **Done.** I've implemented the user authentication flow, added tests, and updated `ARCHITECTURE.md`.
>
> **How to verify:**
> ```bash
> # Install dependencies
> uv sync
>
> # Apply migrations
> docker compose up -d postgres
> alembic upgrade head
>
> # Run the test suite
> pytest tests/unit/
> pytest tests/integration/  # requires running Docker services
>
> # Start the full stack
> docker compose up --build
>
> # Smoke test the endpoint
> curl -X POST http://localhost:8000/auth/login \
>   -H "Content-Type: application/json" \
>   -d '{"email": "test@example.com", "password": "secret"}'
> ```

Never commit or push changes yourself unless the user explicitly instructs you to.

### Ambiguity Resolution
Not every unknown warrants stopping to ask. Use this to decide:

- **Ask first** if the ambiguity affects the data model, a service boundary, an external interface (API contract, DB schema), or a choice that would be expensive to reverse.
- **Decide and document** if the ambiguity is an internal implementation detail within an already-agreed design. Make the most reasonable choice, then state it explicitly in the completion summary so the user can review and correct it if needed.

When in doubt about which category an ambiguity falls into, default to asking.

### Protected Files
The following files carry outsized risk if edited carelessly. **Always confirm with the user before modifying them**, even if the change seems minor:

- `ARCHITECTURE.md`
- `pyproject.toml` / `setup.cfg` / `setup.py`
- `Dockerfile` / `docker-compose.yml` / any `docker-compose.*.yml`
- `.env` / `.env.example`
- Any Alembic migration file under `migrations/versions/`
- `conftest.py` at the project root

### Discovered Problems
If you notice a bug, a rule violation, or a significant code smell in code you were not asked to touch, **do not fix it silently**. Flag it clearly in the completion summary with a brief description and its location but do not fix it unless it prevents your current task from running. Do not expand the scope of the current task to address it unless the user explicitly asks you to.

---

## Version Control

### Branching Strategy
- The stable, up-to-date code lives in the `master` branch. **Never push directly to `master`.**
- For every new task, create a branch using this naming format:

```
<type>/<short-description>
```

Where `<short-description>` is a concise kebab-case summary of the work and `<type>` is one of:

| Type | When to use |
|---|---|
| `feature/` | New functionality or major improvements |
| `bugfix/` or `fix/` | Fixing bugs |
| `hotfix/` | Urgent, high-priority fixes (typically for production) |
| `docs/` | Documentation changes (README, API docs, ARCHITECTURE.md, etc.) |
| `chore/` | Maintenance tasks such as updating dependencies |
| `experiment/` | Exploratory work or prototyping new ideas |

Examples: `feature/oauth-flow-implementation`, `fix/token-expiry-edge-case`, `chore/update-pydantic-v2`, `docs/api-reference-update`.

---

## Language

- The primary language for this project is **Python**. Target specifically Python 3.13 version or higher.
For checking on 3.13 release changes/features check this page: https://docs.python.org/3.13/whatsnew/3.13.html
---

## Code Style & Design Principles

### Package Management
Use **`uv`** instead of `pip` for all package installation and virtual environment management, but never install packages to host OS global Python installation. It is significantly faster, produces reproducible installs, and handles locking correctly. Use `uv` in `Dockerfile` layers as well.

```dockerfile
RUN pip install uv
RUN uv sync
```

Never use bare `pip install` in code, scripts, or documentation. If you need to reference installation instructions, always use the `uv` equivalent.

uv commands cheatsheet to re-cap: https://mathspp.com/blog/uv-cheatsheet

### Formatting & Linting
- Use **4 spaces** for indentation, not tab.
- Use **Ruff** for both linting and formatting. It replaces Pylint, Flake8, isort, and Black in a single fast tool. All code must pass `ruff check` and `ruff format --check` with no errors before a task is considered complete.
- Configure Ruff in `pyproject.toml`. Enable at minimum the `E`, `F`, `I`, and `UP` rule sets. Expand coverage (e.g., `B`, `C4`, `SIM`) as the project matures.

```toml
[tool.ruff]
indent-width = 4  # Ruff uses spaces internally but respects your style config

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "C4", "SIM"]

[tool.ruff.format]
indent-style = "space"
```

- If a rule must be suppressed for a justified reason, disable it at the narrowest possible scope using a `# noqa` comment and include an explanation:

```python
result = some_call()  # noqa: SLF001  # accessing private attr required by framework X
```

- Never suppress a rule globally unless it conflicts with an immovable project-wide constraint. Discuss with the user first.

### Naming
- Never use single-character variable names except:
  - `i`, `j`, `k` as loop indices.
  - Inside list/dict/set comprehensions or generator expressions where the variable scope is limited to that expression.
  - Mathematical contexts where single-letter names are conventional and unambiguous (e.g., `x`, `y` for coordinates).
- All other variables, parameters, and attributes must have descriptive names that clearly communicate intent.

### Constants
Define constants in exactly one of these three places depending on their scope:

| Scope | Location |
|---|---|
| Used across the package | `constants.py` in the package root |
| Used only within one module | Top of that module, after imports |
| Used only within one function/method | Top of that function/method body |

Constants must be named in `UPPER_SNAKE_CASE`. Never scatter magic values inline — always extract them.

### DRY (Don't Repeat Yourself)
Actively identify and eliminate repetitive patterns. Before writing new logic, check whether an equivalent already exists. If a pattern appears more than once, extract it.

### Explicit Over Implicit
Code must be transparent and easy to reason about:
- Use **dependency injection** to make coupling visible and testable — pass dependencies in, don't reach out for them.
- Keep **control flows obvious** — a reader must be able to follow the logic without hunting through the codebase.
- Avoid "magic" initialization patterns such as **Singletons** or module-level side effects that introduce hidden state.

### Single Responsibility Principle
Each function, method, and class must do one thing. If you find yourself writing "and" when describing what a unit does, split it.

### Guard Clauses
Handle edge cases, invalid inputs, and early exits at the top of a function. Do not wrap the happy path in conditionals — let it flow naturally at the end.

```python
# Correct
def process(user: User) -> Result:
	if not user:
		raise ValueError("user is required")
	if not user.is_active:
		raise PermissionError("user is not active")

	return do_work(user)

# Wrong
def process(user: User) -> Result:
	if user:
		if user.is_active:
			return do_work(user)
```

### Avoid Nested Conditionals
Nesting `if` statements is a sign that logic needs to be restructured. Use guard clauses, early returns, or extract helpers instead.

---

## Imports

Run ruff or isort to handle imports automatically before submitting. The right order looks as follows:

```python
# 1. Built-in packages
import os
import sys

# 2. Third-party packages
import httpx
from pydantic import BaseModel

# 3. Own/custom packages
from myproject.core import something
```

Additional rules:
- **Do not place imports inside functions or methods** unless there is a strong, specific justification (e.g., resolving a circular import that cannot be addressed structurally).
- If you believe an in-function import is warranted, **stop, explain the justification to the user, and wait for explicit approval** before proceeding.
- **Do not introduce dead imports.** Every imported name must be used.

---

## Dead Code

Do not leave dead code in the codebase — no unused functions, variables, commented-out blocks, or unreachable branches. If something is being removed, remove it fully.

---

## Type Annotations

- **All** functions and methods must have type annotations on parameters and return values.
- Use annotations actively during implementation — if a type doesn't fit, treat it as a signal to reconsider the design, not something to cast or ignore.
- Use `from __future__ import annotations` at the top of files where forward references are needed.

```python
# Correct
def get_user(user_id: int) -> User:
	...

# Wrong
def get_user(user_id):
	...
```

---

## Error Handling

### Avoid Generic Exceptions
Do not raise or catch `Exception` or `BaseException` unless there is an explicit, justified reason. Use the most specific exception type available. Define custom exception classes when built-ins don't communicate the domain error clearly enough.

```python
# Correct
raise ValueError(f"Invalid configuration key: {key!r}")

# Wrong
raise Exception("something went wrong")
```

When catching, be equally specific:

```python
# Correct
try:
	result = fetch_data(url)
except httpx.TimeoutException:
	logger.warning("Request timed out", extra={"url": url}, exc_info=True)
	return None

# Wrong
try:
	result = fetch_data(url)
except Exception:
	pass
```

### Catch vs. Propagate — Decision Guide

**Scenario 1 — Catch: you can recover and the caller doesn't need to know**
A cache miss during a read. The function falls back to the database. The error is an implementation detail — catch it locally and continue.
```python
def get_user(user_id: int) -> User:
	try:
		return cache.get(user_id)
	except CacheMissError:
		return db.query_user(user_id)
```

**Scenario 2 — Catch: translate a low-level error into a domain error**
A database `IntegrityError` is a storage detail. The service layer must not leak it. Catch and re-raise as a meaningful domain exception, preserving the original cause with `from`.
```python
def create_user(email: str) -> User:
	try:
		return db.insert_user(email)
	except IntegrityError as error:
		raise DuplicateEmailError(email) from error
```

**Scenario 3 — Propagate: the caller is responsible for the decision**
A file not found during a user-initiated operation. Whether to retry, skip, or abort is the caller's business — don't swallow it.
```python
def load_config(path: Path) -> Config:
	# Let FileNotFoundError propagate — the caller decides what to do.
	raw = path.read_text()
	return Config.parse(raw)
```

**Scenario 4 — Propagate: you have no useful recovery action**
Catching an error only to log and re-raise adds noise without value. Let it propagate and handle logging at the boundary where a decision can actually be made.
```python
# Wrong — adds nothing
try:
	do_work()
except SomeError as error:
	logger.error(error)
	raise
```

**Scenario 5 — Catch at the boundary: prevent crashes in top-level handlers**
HTTP request handlers, job runners, and similar entry points. Catch broadly here — and only here — to return a clean response or log a structured failure before continuing to process other requests or jobs.
```python
@app.post("/process")
def process_endpoint(payload: Payload) -> Response:
	try:
		result = service.process(payload)
		return Response(result)
	except DomainError as error:
		return ErrorResponse(status=400, detail=str(error))
	except Exception:
		logger.exception("Unexpected error processing payload", extra={"payload": payload})
		return ErrorResponse(status=500, detail="Internal server error")
```

---

## Logging

Use **structured logging** throughout. Every log entry must carry enough context to be useful in isolation — avoid freeform messages that require surrounding context to interpret.

### Log Levels

**`DEBUG`** — Low-level operational detail. Useful during development and deep troubleshooting. Not expected in normal production output. Use for:
- A model, client, connection pool, or heavy component was successfully initialized or loaded.
- An outbound request was dispatched (log method, URL, and relevant parameters).
- Internal state transitions within a complex workflow.
- Cache hit or miss events.

**`INFO`** — Confirmation that the system is behaving as expected. Use for:
- A query completed and returned N records.
- No records found for a given input (a valid empty result, not an error).
- A retry attempt: attempt N of M, next retry in T seconds.
- An operation completed successfully (file written, message published, job finished).

**`WARNING`** — Something unexpected or potentially problematic occurred, but execution can continue. Always warrants attention. Use for:
- A caught exception in a recoverable code path — always include `exc_info=True` to preserve the traceback.
- Use of a deprecated library, API endpoint, or internal component.
- A configuration value is missing and the code fell back to a default.
- A soft resource limit is approaching (e.g., connection pool nearly exhausted, low disk space).
- An external dependency responded slowly but within an acceptable threshold.

**`ERROR`** — A failure that cannot be recovered from locally. All exceptions that propagate to a top-level boundary handler must be logged here. Use for:
- An unhandled exception in a request handler or job runner (use `logger.exception` — it captures the full traceback automatically).
- Failure to connect to a required external service after retries are exhausted.
- Data integrity violations that cannot be resolved automatically.

### Rules
- Use `logger.exception(...)` inside `except` blocks at error boundaries — it automatically captures the traceback. Prefer it over `logger.error(..., exc_info=True)`.
- Use `logger.warning(..., exc_info=True)` when logging a caught exception that allows execution to continue.
- **Never use `print()` for diagnostic output.** Always use the logger.
- Pass context as structured `extra` fields, not string concatenation:

```python
# Correct — structured extra fields
logger.info("Query completed", extra={"record_count": count, "table": table_name})

# Also acceptable — % formatting (lazy evaluation, ruff-friendly)
logger.info("Query returned %d records from %s", count, table_name)

# Wrong — string concatenation
logger.info("Query returned " + str(count) + " records from " + table_name)
```

### Logger Setup
- Every module must obtain its logger via `logging.getLogger(__name__)`. This names the logger after the module path, making log output easy to trace back to its source.
- **Never call `logging.basicConfig()` inside library or application modules.** Logging configuration belongs in one place: the application entry point (e.g., `main.py` or the container startup script).
- Use `python-json-logger` (or equivalent) to emit logs as structured JSON. This makes logs parseable by log aggregators (Datadog, Loki, CloudWatch, etc.) without post-processing.
- The log level must be controlled via the `LOG_LEVEL` environment variable, defaulting to `INFO`. Never hardcode a level.

Minimal setup pattern — entry point only:
```python
import logging
import os
from pythonjsonlogger import jsonlogger

def configure_logging() -> None:
	log_level = os.getenv("LOG_LEVEL", "INFO").upper()
	handler = logging.StreamHandler()
	handler.setFormatter(jsonlogger.JsonFormatter())
	logging.root.setLevel(log_level)
	logging.root.addHandler(handler)
```

Every module:
```python
import logging

logger = logging.getLogger(__name__)
```

---

## Testing

### Framework
Use **pytest** for all tests. Do not use `unittest` unless integrating with a library that explicitly requires it.

### Coverage
Maintain a minimum of **90% code coverage**. New code submitted without tests that meet this threshold is incomplete.

Configure coverage in `pyproject.toml`:
```toml
[tool.pytest.ini_options]
addopts = "--cov=myproject --cov-report=term-missing --cov-fail-under=90"
```

### Conventions
- **One test file per module**: `myproject/core/parser.py` → `tests/core/test_parser.py`. The `tests/` directory must mirror the package structure exactly.
- **Separate unit and integration tests** into distinct subdirectories: `tests/unit/` and `tests/integration/`. Unit tests must run without any external services (no database, no network). Integration tests may require a running environment (use Docker Compose for this).
- **Shared fixtures live in `conftest.py`** — at the appropriate level. Project-wide fixtures go in the root `conftest.py`; fixtures specific to a subdirectory go in that subdirectory's `conftest.py`.
- **Name tests to describe behavior**, not implementation: `test_returns_none_when_user_is_inactive`, not `test_process_2`.
- **Mock at the boundary**: mock external I/O (HTTP, DB, filesystem), not internal implementation details. Prefer pytest-mock (mocker fixture) over unittest.mock. Do not use sleep() in tests to wait for async events; use polling or event loops.
- **Use `pytest.raises`** for exception assertions — never use bare `try/except` inside tests.
- **Parametrize** repeated test logic with `@pytest.mark.parametrize` instead of copy-pasting test cases.
- Keep each test focused on **one behavior**. Multiple assertions about a single outcome are fine. Testing multiple unrelated outcomes in one test is not — split it.

```python
# Good
@pytest.mark.parametrize("email", ["", "notanemail", "a@", "@b.com"])
def test_rejects_invalid_emails(email: str) -> None:
	with pytest.raises(ValueError):
		validate_email(email)
```

---

## Docker & Deployment

Every service in this project is containerized and runs via Docker Compose. This is not optional — implementations must be designed to run correctly inside containers from the start, not adapted afterward.

### Design for Containers First
- Code must never assume it is running on a host machine. Paths, ports, hostnames, and service addresses are all container-relative.
- Services communicate with each other using Docker Compose service names as hostnames (e.g., `postgres`, `redis`), not `localhost` or `127.0.0.1`. Assume the application runs on 0.0.0.0, not 127.0.0.1, within the container.
- Never hardcode `localhost` for any inter-service communication. It will silently fail inside a container network.

### Paths
- Never hardcode absolute paths. All paths must be derived from environment variables or anchored to a well-known relative root.
- Use `pathlib.Path` for all path construction and manipulation — never string concatenation.
- When a path must be configurable between environments (e.g., a model directory, a data volume mount), expose it as an environment variable and document it in `.env.example`.

### Environment Variables
- All configuration that differs between environments (dev, test, prod) must come from environment variables — including database URLs, service hostnames, ports, credentials, feature flags, and log levels.
- Document **every** required variable in `.env.example` at the project root, with a comment explaining what each does and an example value. A new developer (or a container) must be able to read `.env.example` and know exactly what to provide.
- In `docker-compose.yml`, pass variables explicitly using the `environment:` or `env_file:` key. Do not rely on variables leaking through from the host shell implicitly.
- Use Pydantic `BaseSettings` to load and validate all environment variables at application startup. If a required variable is missing or malformed, the application must fail fast with a clear error — not silently use a wrong default.

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
	database_url: str
	log_level: str = "INFO"
	model_dir: Path = Path("/app/models")

settings = Settings()
```

> **Note for Docker:** Do NOT use `env_file = ".env"` in pydantic-settings when running in containers. Docker Compose already passes `.env` as environment variables automatically. Pydantic-settings reads environment variables directly without needing the env_file config.

### Optimizing Build Time
Structure `Dockerfile` stages to maximize Docker layer cache reuse:
- Copy dependency manifests (`pyproject.toml`, `uv.lock`) and install dependencies **before** copying application code. Dependency layers are only rebuilt when dependencies change, not on every code edit.
- Use UV cache mount to avoid re-downloading packages between builds.
- Pre-download heavy artifacts (ML models, large datasets, compiled binaries) in a dedicated `Dockerfile` stage or a separate Docker Compose init service. These must not be re-downloaded on every build or container restart.
- If an artifact can be baked into an image layer, prefer it. If it is too large, store it in a named Docker volume so it persists across restarts and rebuilds.

See "Service Dockerfile Template" above for the recommended pattern.

### Health Checks
Every long-running service must define a `healthcheck` in `docker-compose.yml`. Dependent services must use `depends_on: condition: service_healthy` rather than `depends_on` alone. Starting order without health checks leads to race conditions that are hard to debug.

### Service Dockerfile Template
Use this pattern for new Python services. This template uses `uv` for dependency management and includes proper layer caching.

```dockerfile
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# 1. Dependencies layer — cached unless pyproject.toml or uv.lock changes
COPY service/pyproject.toml service/uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# 2. Source code layer — invalidated on every code change
COPY shared/shared ./shared/
COPY service/service ./service/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["uvicorn", "service.service.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Important:**
- Always run `uv lock` before first build to generate `uv.lock`
- Copy both `pyproject.toml` and `uv.lock` together for proper caching
- Use `--frozen` to ensure reproducible builds
- Include `--mount=type=cache,target=/root/.cache/uv` to cache downloaded packages between builds

### Dependencies from shared/ Package
When a service imports from the `shared/` package (models, database connection), you MUST analyze what dependencies the imported code requires. The shared package itself does not declare runtime dependencies — each service must declare them explicitly.

Example: importing `shared.models.topic` requires:
- `sqlalchemy[asyncio]` — ORM
- `asyncpg` — Async PostgreSQL driver
- `pgvector` — Vector column type

Always check the import chain and add all required dependencies to the service's `pyproject.toml`.

### Large Dependency Warning
**Before using PyTorch, TensorFlow, or any heavy ML library, you MUST:**
1. Warn the user about the impact on Docker image size (PyTorch adds ~7GB)
2. Get explicit permission to proceed
3. Consider CPU-only variants to reduce size (e.g., use CPU-only PyTorch index)

Example for CPU-only PyTorch in pyproject.toml:
```toml
[tool.uv.sources]
torch = [
  { index = "pytorch-cpu" },
]

[[tool.uv.index]]
name = "pytorch-cpu"
url = "https://download.pytorch.org/whl/cpu"
explicit = true
```

---

## Technology Defaults

These are the default choices for common concerns. Deviating from them is allowed only when there is a clear, specific reason the default does not fit — in which case, explain the reason to the user and get approval before proceeding.

### Database
**PostgreSQL** is the default database choice. Use it unless the task has requirements that PostgreSQL demonstrably cannot meet (e.g., a graph database for a heavily connected dataset, or an embedded database for an offline-first CLI tool). Do not reach for an alternative simply because it seems simpler or more familiar for the task at hand.

### Data Access
**Prefer ORM over raw SQL.** Raw queries are harder to compose, test, and refactor safely. Use:
- **SQLAlchemy** for relational databases — it is mature, well-documented, and integrates well with the rest of the Python ecosystem.
- An equivalent mature library for non-relational databases (e.g., Motor for MongoDB, redis-py for Redis).

Raw SQL is acceptable when a query is genuinely too complex or performance-sensitive to express cleanly through the ORM, and only after confirming with the user.

### Database Migrations
Use **Alembic** for all PostgreSQL schema migrations. Rules:
- **Never modify the database schema directly** — all schema changes must go through a migration file.
- Every migration must be reversible. Always implement both `upgrade()` and `downgrade()`.
- Migration files are **protected** — see the Protected Files section. Do not edit an existing migration that has already been applied; create a new one instead.
- Name migrations descriptively: `alembic revision --autogenerate -m "add_user_roles_table"` not `"fix"` or `"update"`.

### Serialization, Deserialization & Validation
Use **Pydantic** for all serialization, deserialization, and input validation. It integrates naturally with type annotations, produces clear validation errors, and reduces boilerplate. Do not implement manual validation logic for data that Pydantic can handle.

### Configuration Management
Use **Pydantic `BaseSettings`** (`pydantic-settings` package) to load and validate all application configuration from environment variables. This gives you type-safe config with validation at startup, a single place to see every configurable value, and natural `.env` file support for local development.

- Define a single `Settings` class (or a small set of domain-grouped ones) and instantiate it once at startup. Inject it where needed — do not import it as a global throughout the codebase.
- If a required variable is absent or invalid, the application must **fail fast at startup** with a clear error message, not fail silently at runtime when the value is first used.
- Keep the `Settings` class in a dedicated `config.py` module.

---

## Philosophy

- **No premature optimization.** Write clean, correct, readable code first. Optimize only when there is a measured, demonstrable performance problem. An elegant, well-understood solution that is slightly slower is preferable to a clever one that is brittle or hard to reason about.
- **Prefer time-proven approaches.** Default to established patterns and well-maintained libraries. Reach for novel or experimental solutions only when they offer a significant, concrete benefit that the conventional approach cannot provide.
- **Keep things smart and simple.** Complexity must earn its place. If a simpler approach works, use it.
- **When in doubt about a design decision, ask before implementing.**
