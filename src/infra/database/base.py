from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from src.config import get_settings

settings = get_settings()

engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")
SessionFactory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


if settings.database_url:
    engine = create_async_engine(
        str(settings.database_url),
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        echo=settings.app_debug,
    )
    async_session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
else:
    engine = None  # type: ignore[assignment]
    async_session_factory = None  # type: ignore[assignment]


async def get_session():
    """Yield a raw database session. No transaction management."""
    if async_session_factory is None:
        yield None
        return

    async with async_session_factory() as session:
        yield session
