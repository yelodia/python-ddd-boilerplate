from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class Command(BaseModel):
    pass


class UseCase(ABC):
    """Базовый класс для всех юзкейсов."""

    cmd: type[Command] = Command

    @abstractmethod
    async def execute(self, cmd: Command) -> Any:
        raise NotImplementedError
