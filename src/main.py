import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from arq import create_pool
from arq.connections import RedisSettings
from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from redis.asyncio import Redis

from api.rest.items.views import items_router
from api.rest.items.ws_views import items_ws_router
from api.rest.posts.views import posts_router
from api.rest.root_error_handlers import bind_error_handlers_to
from api.rest.shop.views import products_router, carts_router
from api.rest.shop.ws_views import shop_ws_router
from config import get_settings
from infra.middleware.correlation import CorrelationMiddleware
from infra.middleware.logging import LoggingMiddleware
from infra.observability.logging import setup_logging
from infra.observability.tracing import setup_tracing
from infra.storage.json_storage.setup import ensure_json_storage
from infra.ws.pubsub_listener import ws_pubsub_listener
from infra.ws_manager import ws_manager


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    setup_logging()
    setup_tracing(app)

    settings = get_settings()
    if settings.use_json_storage:
        ensure_json_storage(settings.json_data_dir)

    app.state.arq_pool = await create_pool(RedisSettings.from_dsn(str(settings.redis_url)))

    # Отдельный Redis-клиент для pub/sub подписки (ArqRedis не подходит для длинных подписок)
    pubsub_redis = Redis.from_url(str(settings.redis_url))
    pubsub_task = asyncio.create_task(ws_pubsub_listener(ws_manager, pubsub_redis))

    yield

    pubsub_task.cancel()
    try:
        await pubsub_task
    except asyncio.CancelledError:
        pass
    await pubsub_redis.aclose()
    await app.state.arq_pool.aclose()


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="My App",
        version="0.1.0",
        debug=settings.app_debug,
        docs_url=None if settings.is_production else "/docs",
        redoc_url=None if settings.is_production else "/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(LoggingMiddleware)
    app.add_middleware(CorrelationMiddleware)

    bind_error_handlers_to(app)

    # подготовка "большого" роутера - все включенные в него роутеры будут иметь префикс /api/v1
    router = APIRouter(prefix="/api/v1")

    # вьюшки bounded context'а items
    router.include_router(items_router)
    router.include_router(items_ws_router)

    # вьюшки bounded context'а shop
    router.include_router(products_router)
    router.include_router(carts_router)
    router.include_router(shop_ws_router)

    # вьюшки bounded context'а posts
    router.include_router(posts_router)

    # подключение получившегося большого роутера в само fastapi-приложение
    app.include_router(router)

    @app.get("/health", response_model=HealthResponse, tags=["health"])
    async def health_check() -> HealthResponse:
        return HealthResponse()

    return app


application = create_app()
