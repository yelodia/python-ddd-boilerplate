from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager
from typing import Callable


class UnitOfWork(ABC):
    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...

    @abstractmethod
    async def close(self) -> None: ...


UowFactory = Callable[[], AbstractAsyncContextManager[UnitOfWork]]
