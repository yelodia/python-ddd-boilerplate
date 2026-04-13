from abc import ABC, abstractmethod

from core.domain_events import DomainEvent


class EventHandler(ABC):
    """Базовый класс для обработчиков доменных событий."""

    @abstractmethod
    async def handle(self, event: DomainEvent) -> None:
        raise NotImplementedError
