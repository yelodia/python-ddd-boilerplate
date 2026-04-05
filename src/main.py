from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter

from common.exceptions import DomainError
from api.rest.auth.views import router as auth_router
from api.rest.exception_handlers import domain_exception_handler
from api.rest.items.views import router as items_router
from common.schemas import HealthResponse
from config import get_settings
from middleware.correlation import CorrelationMiddleware
from middleware.logging import LoggingMiddleware
from observability.logging import setup_logging
from observability.tracing import setup_tracing


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    setup_logging()
    setup_tracing(app)

    settings = get_settings()
    if settings.use_json_storage:
        from src.infrastructure.file_storage.setup import ensure_json_storage

        ensure_json_storage(settings.json_data_dir)

    yield


async def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="My App",
        version="0.1.0",
        debug=settings.app_debug,
        docs_url=None if settings.is_production else "/docs",
        redoc_url=None if settings.is_production else "/redoc",
        lifespan=lifespan,
    )

    # noinspection PyTypeChecker
    app.add_middleware(LoggingMiddleware)
    # noinspection PyTypeChecker
    app.add_middleware(CorrelationMiddleware)

    # exception handlers used to reduce to a single form of response
    app.add_exception_handler(DomainError, domain_exception_handler)

    router = APIRouter(prefix="/api/v1")
    router.include_router(auth_router)
    router.include_router(items_router)
    app.include_router(router)

    @app.get("/health", response_model=HealthResponse, tags=["health"])
    async def health_check() -> HealthResponse:
        return HealthResponse()

    return app


app = create_app()
