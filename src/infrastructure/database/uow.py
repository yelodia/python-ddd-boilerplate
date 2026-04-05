from contextlib import asynccontextmanager

from infrastructure.database.base import get_session


class UnitOfWork:
    """Manages transaction boundaries on a database session."""

    def __init__(self, session) -> None:
        self.session = session

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()

    async def close(self) -> None:
        await self.session.close()


@asynccontextmanager  # либо можно через __enter__ и __exit__ в самом классе
async def unit_of_work(session):
    uow = UnitOfWork(session)
    try:
        yield uow
        await uow.commit()
    except Exception:
        await uow.rollback()
        raise
    finally:
        await uow.close()
