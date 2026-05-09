# My App

FastAPI · SQLAlchemy 2.0 · PostgreSQL · arq · structlog · OpenTelemetry

---

## Quick Start

### Requirements

- Python 3.14+
- [uv](https://docs.astral.sh/uv/#installation) — package manager
- Docker & Docker Compose (для dev-инфраструктуры и prod-стека)

### Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Install dependencies

```bash
uv sync --active --extra dev   # dev (тесты, линтер, mypy)
uv sync --active               # prod (без dev-зависимостей)
```

### Check Python version

```bash
uv run --active python --version
```

---

## Development

### 1. Start dev infrastructure

Redis (+ PostgreSQL при необходимости) в Docker:

```bash
sudo docker compose -f docker-compose-dev.yml up -d --build
```

### 2. Run application

Все команды запускаются из `src/`:

```bash
cd src

# Web-сервер
uv run --active python -m uvicorn main:create_app --host=127.0.0.1 --port=8081 --reload

# arq воркер cron-задач
uv run --active python ./cron_tasks_worker.py

# arq воркер доменных событий
uv run --active python ./domain_events_worker.py
```

### 3. Run tests

Из корня проекта:

```bash
uv run --active pytest tests/ -v --cov=src --cov-report=term-missing
```

---

## Production

```bash
python -m uvicorn main:create_app --host=127.0.0.1 --port=80
python ./cron_tasks_worker.py
python ./domain_events_worker.py
```

Или полный Docker-стек:

```bash
docker compose up --build -d
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `STORAGE_BACKEND` | `json` | `json` — files, `sql` — PostgreSQL |
| `JSON_DATA_DIR` | `data` | JSON files directory |
| `DATABASE_URL` | — | PostgreSQL URL |
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
├── domain_events_worker.py          # arq worker: domain events
├── cron_tasks_worker.py             # arq worker: cron tasks
│
├── api/                             # PRESENTATION layer
│   ├── dependencies.py              # DI-wiring (FastAPI Depends)
│   └── rest/
│       ├── root_error_handlers.py   # auto-discovery of error handlers
│       └── {domain}/                # items/, shop/, ...
│           ├── views.py             # HTTP endpoints
│           ├── schemas.py           # Pydantic request/response
│           └── error_handlers.py    # domain exceptions → HTTP codes
│
├── application/                     # APPLICATION layer
│   └── {domain}/
│       ├── use_cases.py             # coordination + structured logging
│       └── commands.py              # Pydantic command DTOs
│
├── core/                            # DOMAIN layer
│   └── {domain}/
│       ├── entities.py              # Rich Domain Model (dataclass)
│       ├── exceptions.py            # pure domain exceptions
│       ├── service.py               # business logic (no IO)
│       └── repository.py            # abstract interface (ABC)
│
└── infra/                           # INFRASTRUCTURE layer
    ├── storage/
    │   ├── json_storage/            # JSON file backend
    │   ├── in_memory/               # in-memory backend (tests)
    │   └── database/                # SQL backend (PostgreSQL)
    ├── event_bus/                   # EventBus implementations
    ├── ws/                          # WebSocket publishers
    ├── middleware/                  # correlation ID, request logging
    ├── observability/               # structlog + OpenTelemetry
    └── worker/                      # arq worker settings + tasks
```

See [AGENT_ARCHITECTURE.md](AGENT_ARCHITECTURE.md) for detailed rules and conventions.

---

## Make Commands

```bash
make install          # uv sync (prod)
make install-dev      # uv sync --extra dev
make dev-infra-up     # docker compose -f docker-compose-dev.yml (Redis)
make dev-infra-down   # stop dev infrastructure
make dev              # uvicorn with hot-reload (from src/)
make worker           # arq domain events worker
make cron-worker      # arq cron tasks worker
make start-json       # run with JSON storage backend
make migrate          # alembic upgrade head
make migrate-new name=X  # new migration
make test             # pytest with coverage
make lint             # ruff check + format check
make lint-fix         # ruff autofix
make type-check       # mypy
make up / make down   # full Docker stack
```
