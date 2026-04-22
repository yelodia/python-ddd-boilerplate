from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel as CommandDTO


class UseCase(ABC):
    """Базовый класс для всех юзкейсов."""

    @abstractmethod
    async def execute(self, cmd: CommandDTO) -> Any:
        raise NotImplementedError
