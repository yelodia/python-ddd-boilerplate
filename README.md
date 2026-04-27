# My App

FastAPI · SQLAlchemy 2.0 · PostgreSQL · arq · structlog · OpenTelemetry

---

## Quick Start

### Requirements

- Python 3.12+
- Docker & Docker Compose (optional — only for modes A and full stack)

### Install

```bash
python -m venv .venv
source .venv/bin/activate

make install-dev
cp .env.example .env
```

---

## Run Modes

### Mode C — Phase 1: JSON, no infrastructure (fastest start)

No dependencies needed. Data stored in `data/*.json`.

```bash
# .env: STORAGE_BACKEND=json, DATABASE_URL commented out
make start-json
```

App: http://localhost:8000
Swagger UI: http://localhost:8000/docs

### Mode A — infrastructure in Docker (recommended for development)

```bash
# Terminal 1
make infra-up
make dev

# Terminal 2
make worker
```

First run with DB:
```bash
make infra-up
# In .env: STORAGE_BACKEND=sql, uncomment DATABASE_URL
make migrate
make dev
```

### Mode B — all local, no Docker

```bash
make start-local   # Terminal 1
make worker        # Terminal 2
```

### Full Docker stack (production-like)

```bash
make up      # start all
make logs    # view logs
make down    # stop
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `STORAGE_BACKEND` | `json` | `json` — files, `sql` — PostgreSQL |
| `JSON_DATA_DIR` | `data` | JSON files directory (Phase 1) |
| `DATABASE_URL` | — | PostgreSQL URL (Phase 2) |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis URL for arq |
| `APP_ENV` | `development` | `development` / `staging` / `production` |
| `LOG_LEVEL` | `INFO` | Log level |
| `OTEL_ENABLED` | `false` | Enable OpenTelemetry tracing |

---

## Project Structure

Horizontal layers on top, vertical domain slices inside each layer.
Dependency direction: `api/ → application/ → core/ ← infrastructure/`.

```
src/
├── config.py                        # pydantic-settings, @lru_cache
├── main.py                          # composition root: FastAPI app factory
├── worker.py                        # composition root: arq WorkerSettings
│
├── api/                             # PRESENTATION layer
│   ├── dependencies.py              # DI-wiring (FastAPI Depends)
│   └── rest/
│       ├── exception_handlers.py    # auto-discovery of error handlers
│       └── {domain}/                # items/, auth/, ...
│           ├── views.py             # HTTP endpoints
│           ├── schemas.py           # Pydantic request/response + from_domain()
│           └── error_handlers.py    # domain exceptions → HTTP codes
│
├── application/                     # APPLICATION layer
│   └── {domain}/
│       ├── use_cases.py             # coordination + structured logging
│       └── tasks.py                 # arq background tasks (if needed)
│
├── core/                            # DOMAIN + SERVICE layer
│   └── {domain}/
│       ├── entities.py              # Rich Domain Model (frozen dataclass)
│       ├── exceptions.py            # pure domain exceptions
│       ├── service.py               # business logic (no logger, no IO)
│       └── repository.py            # abstract interface (ABC)
│
├── infrastructure/                  # INFRASTRUCTURE layer
│   ├── database/                    # SQL backend
│   │   ├── base.py                  # engine, session factory
│   │   ├── uow.py                  # Unit of Work (transactions only)
│   │   ├── models/{domain}.py       # SQLAlchemy ORM models
│   │   └── repositories/{domain}.py # SQL repository implementations
│   ├── file_storage/                # JSON backend
│   │   ├── setup.py                 # ensure data dir + seed files
│   │   └── repositories/{domain}.py # JSON repository implementations
│   ├── in_memory/                   # in-memory backend (for tests)
│   │   └── repositories/{domain}.py
│   └── ws_manager.py               # WebSocket ConnectionManager
│
├── middleware/                      # correlation ID, request logging
├── observability/                   # structlog + OpenTelemetry
└── common/                          # shared schemas (HealthResponse, etc.)
```

See [AGENT_ARCHITECTURE.md](../AGENT_ARCHITECTURE.md) for detailed rules and conventions.

---

## Commands

```bash
make dev           # run with hot-reload (Mode A)
make worker        # arq worker
make infra-up      # only Postgres + Redis in Docker
make migrate       # apply migrations
make migrate-new name=add_users  # new migration
make test          # tests with coverage
make lint          # ruff check
make lint-fix      # ruff autofix
make type-check    # mypy
make up            # full Docker stack
make down          # stop Docker stack
make logs          # logs app + worker
```
