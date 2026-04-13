from typing import Callable

from application.event_bus_interface import EventBus
from application.event_bus_stuff import EventHandlersRegistry
from application.event_handler_base import EventHandler
from core.domain_events import DomainEvent

HandlerFactory = Callable[[type[EventHandler]], EventHandler]


class AsyncInProcessEventBus(EventBus):
    """
    Простая реализация EventBus, которая хранит подписчиков и события в памяти.
    Используется отложенная публикация событий, которая должна явно вызываться юзкейсом после commit().
    Это важно для гарантии того, что обработчики будут вызваны строго после завершения всех транзакций, т.е. когда
    данные точно успешно записаны в хранилище => с ними теперь можно спокойно работать, не опасаясь откатов.

    Методам подписки и публикации, в принципе, допустимо быть синхронными, если они только
    пишут логи и меняют in-memory состояния - в этом них нет никакого тяжелого I/O.

    А вот метод для публикации - обязательно должен быть async/await, чтобы обработчики не блокировали поток!
    Потому что в них может содержаться тяжёлый I/O (работа с ФС, БД, http-запросы, etc) и вообще что угодно.
    """

    def __init__(self, handlers_registry: EventHandlersRegistry, handler_factory: HandlerFactory):
        self.handlers_registry = handlers_registry
        self.handler_factory = handler_factory
        self._queue: list[DomainEvent] = []

    async def publish(self, event: DomainEvent) -> None:
        self._queue.append(event)

    async def dispatch_pending(self) -> None:
        while self._queue:
            event = self._queue.pop(0)
            for handler_cls in self.handlers_registry.get(type(event), []):
                handler = self.handler_factory(handler_cls)
                await handler.handle(event)


def async_event_bus_factory(
        handlers_registry: EventHandlersRegistry,
        handler_factory: HandlerFactory,
) -> AsyncInProcessEventBus:
    return AsyncInProcessEventBus(handlers_registry=handlers_registry, handler_factory=handler_factory)
