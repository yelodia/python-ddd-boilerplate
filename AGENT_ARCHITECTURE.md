# AGENT_ARCHITECTURE.md

> **Статус:** обязательный документ. Читается агентом перед каждым заданием.
> Нарушение любого правила из раздела «НЕЛЬЗЯ» — недопустимо, даже если задание
> явно не упоминает архитектуру.

---

## Контекст проекта

FastAPI-приложение с поддержкой REST API, WebSocket, фоновых задач (arq),
структурированных логов (structlog) и распределённого трейсинга (OpenTelemetry).

**Стратегия хранилища — три бэкенда:**
- `STORAGE_BACKEND=json` — данные в `data/*.json`, БД не нужна
- `STORAGE_BACKEND=sql` — PostgreSQL через SQLAlchemy 2.0 async
- `STORAGE_BACKEND=ram` — in-memory (для тестов)

Переключение: одна переменная в `.env`. Бизнес-логика не меняется.

---

## Карта файлов проекта

```
src/
├── config.py                          # pydantic-settings, @lru_cache
├── main.py                            # app factory, lifespan, роутеры
├── domain_events_worker.py            # entry point: arq воркер доменных событий
├── cron_tasks_worker.py               # entry point: arq воркер cron-задач
│
├── api/                               # PRESENTATION layer
│   ├── dependencies.py                # DI-wiring: UseCasesBuilder + build()
│   └── rest/
│       ├── root_error_handlers.py     # domain exceptions → HTTP codes
│       └── {domain}/
│           ├── views.py               # HTTP endpoints
│           ├── ws_views.py            # WebSocket endpoints
│           ├── responses.py           # Pydantic response DTO + from_domain()
│           └── error_handlers.py      # domain-specific HTTP-коды / кастомные хэндлеры
│
├── application/                       # APPLICATION layer
│   ├── use_case_base.py               # UseCase ABC: execute(cmd) → Any
│   ├── event_handler_base.py          # EventHandler ABC: handle(event) → None
│   ├── event_bus_interface.py         # EventBus ABC: publish(event)
│   ├── uow_interface.py              # UnitOfWork ABC + UowFactory typedef
│   ├── ws_publisher_interface.py      # WsPublisher ABC
│   └── {domain}/
│       ├── use_cases.py               # координация + логирование
│       ├── commands.py                # command DTOs (Pydantic models)
│       └── event_handlers.py          # обработчики доменных событий
│
├── core/                              # DOMAIN layer
│   ├── entity_base.py                 # Entity, Aggregate, ValueObject
│   ├── domain_events.py               # DomainEvent (frozen dataclass, uuid7)
│   ├── exceptions.py                  # DomainError, NotFoundError и пр.
│   └── {domain}/
│       ├── entities.py                # сущности, агрегаты, объекты-значения
│       ├── events.py                  # доменные события
│       ├── exceptions.py              # доменные исключения
│       ├── services.py                # доменный сервис (stateless, без IO)
│       └── repo_interfaces.py         # интерфейс репозитория (ABC)
│
└── infra/                             # INFRASTRUCTURE layer
    ├── usecases_builder.py            # DI-контейнер (рефлексия type hints)
    ├── event_handlers_registry.py     # маппинг событие → обработчики
    ├── ws_events_registry.py          # маппинг событие → WS-уведомление
    ├── ws_manager.py                  # WebSocket ConnectionManager
    ├── middleware/
    │   ├── correlation.py             # X-Request-ID → contextvars
    │   └── logging.py                 # request/response timing
    ├── observability/
    │   ├── logging.py                 # structlog setup: JSON prod / console dev
    │   └── tracing.py                 # OTel TracerProvider + инструментации
    ├── event_bus/
    │   ├── async_in_main_process.py   # обработка событий в рамках запроса
    │   └── async_in_arq_worker.py     # fire-and-forget через Redis/arq
    ├── ws/
    │   ├── pubsub_listener.py         # Redis Pub/Sub для кросс-процессного WS
    │   └── publishers/                # реализации WsPublisher
    ├── worker/
    │   ├── settings.py                # DomainEventsProcessorSettings, CronJobsSettings
    │   ├── tasks/                     # arq-таски обработки событий
    │   └── cron_tasks/                # arq cron-таски
    ├── external_tool/                 # адаптеры внешних API
    ├── reports/                       # реализации ReportStorage
    └── storage/
        ├── database/                  # SQL бэкенд
        │   ├── basic_stuff.py         # engine, session factory
        │   ├── uow.py                # Unit of Work
        │   ├── orm_models/            # SQLAlchemy ORM-модели
        │   └── repositories/          # SQL-реализации репозиториев
        ├── json_storage/              # JSON бэкенд
        │   ├── setup.py               # создание директории + seed
        │   ├── uow.py                # no-op Unit of Work
        │   └── repositories/          # JSON-реализации репозиториев
        └── in_memory/                 # RAM бэкенд (для тестов)
            ├── uow.py                # no-op Unit of Work
            └── repositories/          # in-memory реализации репозиториев
```

---

## Четыре слоя и их правила

### DOMAIN (`core/`) — чистая бизнес-логика
**Файлы:** `entities.py`, `events.py`, `services.py`, `exceptions.py`, `repo_interfaces.py`

```
✅ МОЖНО                              ❌ НЕЛЬЗЯ
────────────────────────────────────  ──────────────────────────────────────
dataclass-сущности с поведением       import fastapi
frozen dataclass для ValueObject      import structlog / logging
frozen dataclass для DomainEvent      import sqlalchemy
бросать доменные исключения           любой IO (файл, сеть, БД)
объявлять ABC репозиториев            logger.info / print
доменные сервисы (stateless)          HTTPException
                                      знание про JSON, SQL или RAM
```

**Сущности** — `@dataclass(kw_only=True)`, наследники `Entity` или `Aggregate`. Мутабельные, содержат бизнес-методы. Не frozen.

**Объекты-значения** — `@dataclass(frozen=True)`, наследники `ValueObject`. Иммутабельные.

**Как отличить Entity от ValueObject:**

Entity — это «кто/что». Имеет идентичность: два объекта с одинаковыми полями, но разными ID — разные сущности. Примеры: Product (конкретный товар на полке), Transaction (конкретная покупка), PriceSnapshot (конкретный снимок цен).
- Вопрос-тест: «может ли существовать два экземпляра с одинаковыми данными, которые при этом являются разными вещами?» Если да — Entity.
- Иммутабельность не является критерием. Product остаётся Entity, даже если бизнес решит убрать обновление. Transaction — Entity, хотя никогда не модифицируется.

ValueObject — это «какой/сколько». Определяется только значениями полей: два адреса с одинаковыми полями — один и тот же адрес. Примеры: DeliveryAddress (описывает куда), PortfolioAsset (описывает сколько чего), CartItem (описывает что в корзине).
- Вопрос-тест: «важна ли мне именно *эта* штука, или только её содержимое?» Если только содержимое — VO.

**Доменные события** — `@dataclass(frozen=True, kw_only=True)`, наследники `DomainEvent`. Содержат минимум данных (ID + ключевые факты). Паттерн «thin beacon».

**Доменные сервисы** — stateless-классы со `@staticmethod`-методами. Правило пустого конструктора: если в конструктор хочется передать репозиторий, логгер или клиент — это не доменный сервис.

---

### INFRASTRUCTURE (`infra/`) — реализации IO
**Файлы:** `storage/*/repositories/`, `usecases_builder.py`, `ws_manager.py`, `event_bus/`, ORM-модели

```
✅ МОЖНО                              ❌ НЕЛЬЗЯ
────────────────────────────────────  ──────────────────────────────────────
aiofiles, asyncpg, SQLAlchemy         бизнес-логика
маппинг ORM/dict → domain объект      HTTPException
всё что имеет side effects            вызов доменного сервиса
```

**Правило маппинга:** каждый репозиторий содержит `_to_domain()` —
единственное место преобразования сырых данных в доменный объект.

---

### APPLICATION (`application/`) — координация сценариев
**Файлы:** `use_cases.py`, `commands.py`, `event_handlers.py`

```
✅ МОЖНО                              ❌ НЕЛЬЗЯ
────────────────────────────────────  ──────────────────────────────────────
вызывать репозитории напрямую          прямые SQL-запросы
вызывать доменный сервис               HTTPException
structlog логирование                  маппинг domain → response DTO
координировать несколько доменов       бизнес-правила (это в сущностях/сервисе)
оборачивать в UoW-транзакции
публиковать события в EventBus
```

Юзкейсы возвращают **доменные объекты**, а не response DTO.

---

### PRESENTATION (`api/`) — HTTP-слой
**Файлы:** `views.py`, `ws_views.py`, `responses.py`, `error_handlers.py`

```
✅ МОЖНО                              ❌ НЕЛЬЗЯ
────────────────────────────────────  ──────────────────────────────────────
парсить HTTP-запрос                   бизнес-логика
вызывать use_cases                    прямой вызов доменного сервиса
маппинг domain → response DTO         прямой вызов репозитория
указывать response_model
WebSocket accept/disconnect
```

По умолчанию views не логирует — бизнесовые логи пишутся в use_cases,
HTTP-запросы/ответы логируются middleware. Но при необходимости (например, дебаг
парсинга WebSocket-сообщений) логирование во views допустимо — это внешний слой.

Маппинг `from_domain()` вызывается **здесь**, во views:
```python
item = await use_case.execute(cmd)
return ItemResponse.from_domain(item)
```

---

## Строгие правила (НЕЛЬЗЯ нарушать никогда)

### Правило 1. Domain не знает о HTTP и IO

В `entities.py`, `services.py`, `events.py` **никогда** нет:
- `import fastapi` или `HTTPException`
- `import structlog`, `logging`, `print`
- `import sqlalchemy`, `aiofiles`, `json`, `open`

### Правило 2. Где можно логировать

Логирование разделяется на два вида:

**Бизнесовые логи** — только в `application/` (use_cases, event_handlers):
```python
# ✅ use_cases.py — результат бизнес-операции
logger.info("item_created", item_id=new_item.id)

# ✅ event_handlers.py — результат обработки события
logger.info("пополнение завершено", count=len(replenished))
```

**Технические/инфраструктурные логи** — в `infra/` (middleware, event_bus, ws_manager, worker):
```python
# ✅ infra/middleware/logging.py — HTTP request/response
logger.info("request", method=method, path=path, status=status_code)

# ✅ infra/ws_manager.py — подключение/отключение WS-клиентов
logger.debug("ws: client connected", topic=topic)

# ✅ infra/worker/tasks/ — ошибки обработки событий
logger.error("Unknown Event, skipping", event_key=event_key)
```

**Presentation** (`api/`) — по умолчанию не логирует (HTTP-уровень покрыт middleware).
Допустимо в исключительных случаях — это внешний слой, не доменный.

**Запрещено** — в `core/` (entities, services, events, exceptions):
```python
# ❌ core/*/entities.py или services.py
logger.info("item_created", ...)  # НЕЛЬЗЯ — домен чист от IO
```

### Правило 3. Три типа объектов — не смешивать

| Объект | Где живёт | Кто видит |
|---|---|---|
| `Item`, `Product`, `Cart` (dataclass) | `core/*/entities.py` | use_cases, views (для from_domain), repository |
| `ItemResponse` (Pydantic) | `api/rest/*/responses.py` | views → HTTP response |
| ORM-модель (SQLAlchemy) | `infra/storage/database/orm_models/` | только репозиторий |

```python
# ✅ Правильная цепочка
# repository: ORM/dict → Item (через _to_domain)
# use_case:   работает с Item, возвращает Item
# views:      Item → ItemResponse (через from_domain) → HTTP response

# ❌ Нарушение — ORM объект в роутере
@router.get("/")
async def list_items() -> list[ItemModel]:  # ORM модель, НЕЛЬЗЯ
    ...
```

### Правило 4. Зависимость только от абстракции

```python
# ✅ use_cases.py
class CreateItemUseCase(UseCase):
    def __init__(self, repo: ItemRepository, uow: UowFactory): ...

# ❌ — привязка к реализации
class CreateItemUseCase(UseCase):
    def __init__(self, repo: JsonItemRepository): ...
```

### Правило 5. Переключение хранилища — только в UseCasesBuilder

`infra/usecases_builder.py` — единственное место, где выбирается реализация репозитория по `STORAGE_BACKEND`. Три словаря (`SQL`, `JSON`, `RAM`) маппят интерфейс → реализацию. Нигде больше в коде не должно быть условия `if storage_backend == ...`.

### Правило 6. Синхронный IO внутри async def — по умолчанию запрещён

```python
# ✅ Правильно — aiofiles
async def _load(self) -> list[dict]:
    async with aiofiles.open(self.path, encoding="utf-8") as f:
        return json.loads(await f.read())

# ❌ Блокирует event-loop
async def _load(self) -> list[dict]:
    return json.loads(self.path.read_text())  # НЕЛЬЗЯ
```

Если синхронную библиотеку нельзя заменить:
```python
from fastapi.concurrency import run_in_threadpool
result = await run_in_threadpool(sync_function, arg)
```

**Ремарка:** правило строгое для кода, работающего в FastAPI-процессе (эндпоинты, middleware). Для фоновых воркеров (arq cron) допустимы исключения — например, синхронная библиотека в задаче, которая выполняется в отдельном процессе и не обслуживает HTTP-запросы. В спорных случаях уточнять у разработчика.

### Правило 7. async def только при наличии await

```python
# ✅ — есть await
async def get_item(self, item_id: UUID) -> Item:
    return await self.repo.get_by_id(item_id)

# ✅ — нет await, обычный def
def get_builder(request: Request) -> UseCasesBuilder:
    return UseCasesBuilder(arq_client=request.app.state.arq_pool)

# ❌ — async без await, лишний overhead
async def get_builder(request: Request) -> UseCasesBuilder:
    return UseCasesBuilder(arq_client=request.app.state.arq_pool)
```

### Правило 8. Return type hints обязательны везде

```python
# ✅
async def execute(self, cmd: CreateItemCmd) -> Item: ...
async def delete(self, item_id: UUID) -> None: ...

# ❌
async def execute(self, cmd: CreateItemCmd): ...
```

Исключение: `__init__` (тип не нужен).
После любого изменения: `make type-check` — ноль ошибок mypy.

### Правило 9. HTTPException только в error_handlers, не в доменном коде

```python
# ✅ core/*/exceptions.py — доменное исключение
raise ItemNotFoundError(f"Item with ID {item_id} not found")

# ✅ api/rest/root_error_handlers.py — маппинг в HTTP-код
_STATUS_CODES = {
    NotFoundError: status.HTTP_404_NOT_FOUND,
}

# ❌ entities.py / use_cases.py
raise HTTPException(status_code=404, detail="Not found")
```

### Правило 10. ws_manager — в infra, не в домене

`ConnectionManager` не знает про конкретный домен. Импорт из `infra.ws_manager`, не из домена.

### Правило 11. Логи — только structlog, никаких альтернатив

```python
# ✅
import structlog
logger = structlog.get_logger(__name__)
logger.info("event_name", key=value)

# ❌
import logging; logging.info(...)
print(...)
```

`trace_id`, `request_id` инжектируются автоматически через contextvars — не добавлять вручную.
Где именно можно логировать — см. Правило 2.

---

## Алгоритм добавления нового bounded context

Источник: комментарий в `src/api/rest/items/views.py`.

```
1. Создать сущность в core/{domain}/entities.py
2. Создать интерфейс репозитория в core/{domain}/repo_interfaces.py
3. Создать реализации репозитория:
   - infra/storage/json_storage/repositories/{domain}.py
   - infra/storage/in_memory/repositories/{domain}.py
   - infra/storage/database/repositories/{domain}.py (если нужен SQL)
4. Зарегистрировать реализации в infra/usecases_builder.py
   (словари SQL, JSON, RAM: интерфейс → реализация)
5. Создать команды в application/{domain}/commands.py
6. Создать юзкейсы в application/{domain}/use_cases.py
7. Создать views в api/rest/{domain}/views.py
   и response DTO в api/rest/{domain}/responses.py
8. Подключить роутер в src/main.py:
   router.include_router({domain}_router)
9. Если есть доменные события:
   - объявить в core/{domain}/events.py
   - создать обработчики в application/{domain}/event_handlers.py
   - зарегистрировать в infra/event_handlers_registry.py
10. Если нужны WS-уведомления:
    - создать WsNotification в application/{domain}/ws_notifications.py
    - зарегистрировать в infra/ws_events_registry.py
11. make type-check && make lint && make test
```

---

## Алгоритм добавления нового метода в существующий домен

```
1. Добавить @abstractmethod в core/{domain}/repo_interfaces.py
2. Реализовать во всех трёх бэкендах:
   - infra/storage/json_storage/repositories/{domain}.py
   - infra/storage/in_memory/repositories/{domain}.py
   - infra/storage/database/repositories/{domain}.py
3. Добавить бизнес-логику в core/{domain}/entities.py или services.py (без logger)
4. Добавить команду в application/{domain}/commands.py
5. Добавить юзкейс в application/{domain}/use_cases.py (с logger, с UoW, с EventBus)
6. Добавить эндпоинт в api/rest/{domain}/views.py (response_model обязателен)
7. make type-check && make lint && make test
```

---

## Чеклист перед коммитом

```
[ ] make type-check  — ноль ошибок mypy
[ ] make lint        — ноль замечаний ruff
[ ] make test        — все тесты зелёные

Проверить вручную:
[ ] В core/ (entities, services, events) нет import structlog / logger
[ ] В core/ нет HTTPException
[ ] В views.py нет прямых вызовов repository
[ ] Маппинг from_domain() только во views, не в use_cases
[ ] Каждый новый async def содержит хотя бы один await
[ ] Каждая функция имеет return type hint
[ ] Синхронного IO внутри async def нет
[ ] ws_manager импортируется из infra, не из домена
[ ] Переключение хранилища только в usecases_builder.py
[ ] Новый репозиторий реализован во всех трёх бэкендах (JSON, SQL, RAM)
[ ] Новый обработчик событий добавлен в event_handlers_registry.py
```

---

## Справка по стеку

| Компонент | Библиотека | Назначение |
|---|---|---|
| Web-фреймворк | FastAPI | HTTP + WebSocket |
| ORM | SQLAlchemy 2.0 async + asyncpg | PostgreSQL |
| Миграции | Alembic | схема БД |
| Фоновые задачи | arq + Redis | два воркера: события + cron |
| Async file IO | aiofiles | JSON-хранилище |
| Логирование | structlog | JSON prod / console dev |
| Трейсинг | OpenTelemetry | FastAPI + SQLAlchemy + httpx |
| Конфигурация | pydantic-settings | .env + типизация |
| Линтер | ruff | проверка + автоисправление |
| Типы | mypy | статический анализ |
| Тесты | pytest-asyncio + httpx | async TestClient |

---

## Команды разработки

```bash
make install-dev          # установка с dev-зависимостями
make start-json           # запуск с JSON-хранилищем, без инфраструктуры
make dev                  # hot-reload (нужны Postgres+Redis через make infra-up)
make worker               # arq воркер доменных событий
make cron-worker          # arq воркер cron-задач
make infra-up             # поднять Postgres + Redis в Docker
make migrate              # alembic upgrade head
make migrate-new name=X   # новая миграция
make type-check           # mypy src
make lint                 # ruff check + format --check
make lint-fix             # ruff autofix
make test                 # pytest с покрытием
make up                   # полный Docker-стек
make logs                 # логи app + воркеров
```
