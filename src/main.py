from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.rest.auth.views import router as auth_router
from src.api.rest.exception_handlers import collect_exception_handlers
from src.api.rest.items.views import router as items_router
from src.common.schemas import HealthResponse
from src.config import get_settings
from src.middleware.correlation import CorrelationMiddleware
from src.middleware.logging import LoggingMiddleware
from src.observability.logging import setup_logging
from src.observability.tracing import setup_tracing


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    setup_logging()
    setup_tracing(app)

    settings = get_settings()
    if settings.use_json_storage:
        from src.infrastructure.file_storage.setup import ensure_json_storage

        ensure_json_storage(settings.json_data_dir)

    yield


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

    for exc_cls, handler in collect_exception_handlers().items():
        app.add_exception_handler(exc_cls, handler)  # type: ignore[arg-type]

    app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
    app.include_router(items_router, prefix="/api/v1/items", tags=["items"])

    @app.get("/health", response_model=HealthResponse, tags=["health"])
    async def health_check() -> HealthResponse:
        return HealthResponse()

    return app


app = create_app()
