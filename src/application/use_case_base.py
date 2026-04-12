from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager
from typing import Callable

from application.uow_interface import UnitOfWork

UowFactory = Callable[[], AbstractAsyncContextManager[UnitOfWork]]


class UseCase(ABC):
    @abstractmethod
    async def execute(self, *args, **kwargs):
        raise NotImplementedError
