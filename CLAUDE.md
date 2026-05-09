# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Команды

```bash
make install-dev      # uv sync --active --extra dev
make dev-infra-up     # Поднять Redis в Docker (docker-compose-dev.yml)
make dev              # Запуск с hot-reload из src/ (нужен Redis через dev-infra-up)
make start-json       # Запуск с JSON-хранилищем (нужен Redis через dev-infra-up)
make worker           # Запуск arq воркера доменных событий
make cron-worker      # Запуск arq воркера cron-задач
make test             # Запуск всех тестов с покрытием
make lint             # Проверка ruff (линтер + форматтер)
make lint-fix         # Автоисправление lint-ошибок
make type-check       # Запуск mypy
make migrate          # Применить миграции БД (alembic upgrade head)
make migrate-new name=X   # Создать новую миграцию
make up / make down   # Полный Docker-стек (prod)
```

Запуск одного теста:
```bash
uv run --active pytest tests/unit/items/test_service.py -v
uv run --active pytest tests/unit/items/test_service.py::test_name -v
```

Тесты запускаются с `STORAGE_BACKEND=json` и `JSON_DATA_DIR=data/test` (задано в `tests/conftest.py`). Режим async-тестов — `auto` (pytest-asyncio).

## Архитектура

Подробные правила, ограничения слоёв, алгоритмы добавления нового домена и чеклисты — в [AGENT_ARCHITECTURE.md](AGENT_ARCHITECTURE.md). Читай его при любой задаче, затрагивающей архитектуру.

Чистая/гексагональная архитектура с DDD. Направление зависимостей: **`api/ → application/ → core/ ← infra/`**.

### Слои (всё внутри `src/`)

- **`core/`** — Доменный слой. Сущности (frozen dataclasses), доменные события, исключения, ABC репозиториев, доменные сервисы. Нулевая зависимость от инфраструктуры.
- **`application/`** — Юзкейсы (command-driven), обработчики событий, команды-DTO (Pydantic-модели). Определяет интерфейсы EventBus, UnitOfWork, ReportStorage, ExternalToolApiClient.
- **`api/`** — FastAPI REST-эндпоинты и WebSocket-вьюхи, организованные по bounded context'ам (`items/`, `shop/`, `posts/`). Pydantic-схемы ответов. Error handler'ы маппят доменные исключения в HTTP-статусы.
- **`infra/`** — Вся инфраструктура: бэкенды хранилищ, реализации event bus, middleware, observability, конфиг воркеров, WebSocket-менеджер.

### Ключевые паттерны

**Подключаемые бэкенды хранилищ** — Три реализации для каждого репозитория: SQL (PostgreSQL/SQLAlchemy), JSON (файловое хранилище/aiofiles), in-memory (для тестов). Выбирается через переменную окружения `STORAGE_BACKEND` (`sql`, `json`, `ram`).

**`UseCasesBuilder`** (`infra/usecases_builder.py`) — DI-контейнер, который через рефлексию читает type hints конструкторов и автоматически подставляет зависимости (репозитории, UoW, event bus, внешние клиенты). При добавлении нового репозитория его нужно зарегистрировать в словарях `SQL`, `JSON` и `RAM` на уровне класса (маппинг интерфейс → реализация).

**Событийная архитектура** — Доменные сущности эмитят события. Два режима event bus: `AsyncInProcessEventBus` (обработчики выполняются в рамках запроса) и `AsyncArqEventBus` (fire-and-forget через Redis/arq). Маппинг событие → обработчики находится в `infra/event_handlers_registry.py`. События, триггерящие WebSocket-уведомления, регистрируются в `infra/ws_events_registry.py`.

**Unit of Work** — Граница транзакции через async context manager. У каждого бэкенда хранилища своя реализация UoW.

**App factory** — `create_app()` в `src/main.py`. Все маршруты монтируются под `/api/v1`. Lifespan управляет arq-пулом, Redis pub/sub для кросс-процессной рассылки WebSocket-сообщений и настройкой JSON-хранилища.

### Bounded Contexts

- **items** — CRUD для сущности Item. Полное тестовое покрытие (unit + integration).
- **shop** — Products + Carts. Доменный сервис `Shopping` обрабатывает кросс-сущностную логику (например, `put_product_to_cart`). Развитая модель событий.
- **posts** — Интеграция с внешним API через адаптер `ExternalToolApiClient`.
- **reports** — Событийная генерация CSV-отчётов.

### Воркеры (`infra/worker/`)

Фоновые воркеры на базе arq с двумя конфигами: `DomainEventsProcessorSettings` (обработка доменных событий) и `CronJobsSettings` (периодические задачи: пополнение склада, генерация отчётов).

## Tooling

- **uv** — менеджер пакетов и виртуальных окружений (вместо pip/venv)
- **docker-compose-dev.yml** — dev-инфраструктура (Redis), запуск: `make dev-infra-up`
- **docker-compose.yml** — полный prod-стек (Postgres, Redis, app, worker)

## Стиль кода

- Python 3.14+, ruff с line-length 100, правила: `E, F, I, N, UP, B, SIM` (B008 игнорируется)
- mypy с `disallow_untyped_defs = true`, strict mode выключен
- Комментарии в кодовой базе на русском и английском
