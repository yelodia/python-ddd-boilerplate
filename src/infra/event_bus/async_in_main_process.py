from typing import Callable

from application.event_bus_interface import EventBus, EventHandlersRegistry
from application.event_handler_base import EventHandler
from application.ws_publisher_interface import WsPublisher
from core.domain_events import DomainEvent
from infra.ws_events_registry import WsEventsRegistry

# Фабрика хэндлеров получает класс хэндлера и текущий экземпляр шины,
# чтобы хэндлер мог публиковать свои события в ту же очередь.
HandlerFactory = Callable[[type[EventHandler], EventBus], EventHandler]


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

    Цепочки событий поддерживаются: если хэндлер публикует новое событие через ту же шину,
    оно будет обработано рекурсивно — прямо в том же вызове publish().
    """

    def __init__(
            self,
            handlers_registry: EventHandlersRegistry,
            handler_factory: HandlerFactory,
            ws_events_registry: WsEventsRegistry,
            ws_publisher: WsPublisher,
    ):
        self._handlers_registry = handlers_registry
        self._handler_factory = handler_factory
        self._ws_events_registry = ws_events_registry
        self._ws_publisher = ws_publisher

    async def publish(self, event: DomainEvent) -> None:
        # WS первым - он лёгкий, не требует сериализации и round-trip до Redis, потом всё остальное
        await self._notify_ws_subscribers(event)
        await self._run_handlers(event)

    async def _notify_ws_subscribers(self, event: DomainEvent) -> None:
        notification_cls = self._ws_events_registry.get(type(event), None)
        if notification_cls is None:
            return
        notification = notification_cls.from_event(event)
        await self._ws_publisher.notify(notification)

    async def _run_handlers(self, event: DomainEvent) -> None:
        for handler_cls in self._handlers_registry.get(type(event), []):
            handler = self._handler_factory(handler_cls, self)  # передаём себя, чтобы хэндлер мог пушить события
            await handler.handle(event)
