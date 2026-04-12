from contextlib import asynccontextmanager

from application.uow_interface import UnitOfWork


class InMemoryUnitOfWork(UnitOfWork):
    """Concrete implementation of UnitOfWork for in-memory storage."""
    def __init__(self):
        self._data = {}

    async def commit(self) -> None: pass

    async def rollback(self) -> None: pass

    async def close(self) -> None: pass


@asynccontextmanager
async def in_memory_unit_of_work():
    uow = InMemoryUnitOfWork()
    try:
        yield uow
        await uow.commit()
    except Exception:
        await uow.rollback()
        raise
    finally:
        await uow.close()
