from contextlib import asynccontextmanager
from application.uow import UnitOfWork
from infrastructure.database.base import get_session


class SqlUnitOfWork(UnitOfWork):
    """Concrete implementation of UnitOfWork for SQL databases."""

    def __init__(self, session):
        self._session = session

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()

    async def close(self) -> None:
        await self._session.close()


@asynccontextmanager  # либо можно через __enter__ и __exit__ в самом классе
async def sql_unit_of_work(session):
    uow = SqlUnitOfWork(session)
    try:
        yield uow
        await uow.commit()
    except Exception:
        await uow.rollback()
        raise
    finally:
        await uow.close()
