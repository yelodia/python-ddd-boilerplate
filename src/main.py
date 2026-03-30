from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.auth.router import router as auth_router
from src.config import get_settings
from src.exceptions import AppError, app_error_handler
from src.items.router import router as items_router
from src.middleware.correlation import CorrelationMiddleware
from src.middleware.logging import LoggingMiddleware
from src.observability.logging import setup_logging
from src.observability.tracing import setup_tracing


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    setup_logging()
    setup_tracing(app)
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

    app.add_exception_handler(AppError, app_error_handler)  # type: ignore[arg-type]

    app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
    app.include_router(items_router, prefix="/api/v1/items", tags=["items"])

    @app.get("/health", tags=["system"])
    def health() -> dict:
        return {"status": "ok", "version": "0.1.0"}

    return app


app = create_app()
