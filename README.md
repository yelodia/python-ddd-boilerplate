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

```
src/
├── main.py              # entry point, app factory
├── config.py            # settings via pydantic-settings
├── database.py          # SQLAlchemy engine (Phase 2)
├── dependencies.py      # global FastAPI Depends
├── observability/       # structlog + OpenTelemetry
├── middleware/          # correlation ID, request logging
├── infrastructure/      # domain-agnostic infrastructure
│   └── ws_manager.py    # WebSocket ConnectionManager
├── common/              # shared schemas
├── items/               # example domain
│   ├── domain.py        # pure objects and functions (no IO, no logs)
│   ├── schemas.py       # Pydantic API contract (separate from domain)
│   ├── service.py       # pure business logic (no logger)
│   ├── use_cases.py     # coordination + logging + mapping → schemas
│   ├── router.py        # HTTP + WebSocket endpoints
│   ├── repository/      # data layer
│   │   ├── abstract.py  # interface
│   │   ├── json_impl.py # JSON (Phase 1)
│   │   └── sql_impl.py  # PostgreSQL (Phase 2)
│   └── tasks.py         # arq background tasks
└── worker/
    └── settings.py      # arq worker registry
```

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
