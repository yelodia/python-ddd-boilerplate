from abc import ABC, abstractmethod

from application.event_handler_base import EventHandler
from core.domain_events import DomainEvent

EventType = type[DomainEvent]
EventHandlersRegistry = dict[EventType, list[type[EventHandler]]]

class EventBus(ABC):
    """Интерфейс шины доменных событий. Реализации см. в слое инфраструктуры."""

    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """Publish an domain event to the event bus."""
        raise NotImplementedError

    @abstractmethod
    async def dispatch_pending(self) -> None:
        """Dispatch all pending events. Should be called after commit() in use case."""
        raise NotImplementedError
