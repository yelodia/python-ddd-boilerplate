from contextlib import asynccontextmanager

from application.uow import UnitOfWork


class JsonUnitOfWork(UnitOfWork):
    """Concrete implementation of UnitOfWork for JSON file storage."""

    def __init__(self, file_path):
        self._file_path = file_path

    async def commit(self) -> None:
        # Implement logic to write changes to the JSON file
        pass

    async def rollback(self) -> None:
        # Implement logic to discard changes (if necessary)
        pass

    async def close(self) -> None:
        # Implement any cleanup if necessary
        pass


@asynccontextmanager
async def json_unit_of_work(file_path):
    uow = JsonUnitOfWork(file_path)
    try:
        yield uow
        await uow.commit()
    except Exception:
        await uow.rollback()
        raise
    finally:
        await uow.close()
