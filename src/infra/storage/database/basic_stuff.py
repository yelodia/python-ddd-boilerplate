from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from config import settings


class Base(DeclarativeBase):
    pass


_engine = None
_session_factory = None


def get_engine():
    global _engine
    if _engine is None and settings.database_url:
        _engine = create_async_engine(
            str(settings.database_url),
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            echo=settings.app_debug,
        )
    return _engine


def get_session_factory():
    global _session_factory
    if _session_factory is None:
        engine = get_engine()
        if engine is not None:
            _session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return _session_factory


async def get_session():
    """Yield a raw database session. No transaction management."""
    factory = get_session_factory()
    if factory is None:
        yield None
        return
    async with factory() as session:
        yield session
