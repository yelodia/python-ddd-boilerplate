from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from arq import create_pool
from arq.connections import RedisSettings
from fastapi import FastAPI, APIRouter
from pydantic import BaseModel

from api.rest.items.views import router as items_router
from api.rest.root_error_handlers import bind_error_handlers_to
from api.rest.shop.views import products_router, carts_router
from config import get_settings
from infra.middleware.correlation import CorrelationMiddleware
from infra.middleware.logging import LoggingMiddleware
from infra.observability.logging import setup_logging
from infra.observability.tracing import setup_tracing
from infra.storage.json_storage.setup import ensure_json_storage


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    setup_logging()
    setup_tracing(app)

    settings = get_settings()
    if settings.use_json_storage:
        ensure_json_storage(settings.json_data_dir)

    app.state.arq_pool = await create_pool(RedisSettings.from_dsn(str(settings.redis_url)))

    yield

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

    router = APIRouter(prefix="/api/v1")
    router.include_router(items_router)
    router.include_router(products_router)
    router.include_router(carts_router)
    app.include_router(router)

    @app.get("/health", response_model=HealthResponse, tags=["health"])
    async def health_check() -> HealthResponse:
        return HealthResponse()

    return app


application = create_app()
