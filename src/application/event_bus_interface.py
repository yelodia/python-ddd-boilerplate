from abc import ABC, abstractmethod

from application.event_handler_base import EventHandler
from core.domain_events import DomainEvent

EventType = type[DomainEvent]
EventHandlersRegistry = dict[EventType, list[type[EventHandler]]]

class EventBus(ABC):
    """Интерфейс шины доменных событий. Реализации см. в слое инфраструктуры."""

    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """Publish a domain event to the event bus."""
        raise NotImplementedError
