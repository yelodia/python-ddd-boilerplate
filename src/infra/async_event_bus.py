from application.event_bus_interface import EventBus
from application.event_bus_stuff import EventsRegister
from core.domain_events import DomainEvent


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

    def __init__(self, handlers_map: EventsRegister):
        self.handlers_map: EventsRegister = handlers_map
        self._queue: list[DomainEvent] = []

    @classmethod
    def do_something(cls, *args, **kwargs) -> None:
        """
        FIXME глупейшая заглушка-формальность, в которую можно складировать что угодно.
         Например, импорты хэндлеров в main.py только ради того,
         чтобы IDE не сносила импорт как неиспользуемый, а сами хэндлеры за счёт
         наличия таких импортов в main.py - зарегистрировались -_-
        """
        pass

    async def publish(self, event: DomainEvent) -> None:
        self._queue.append(event)

    async def dispatch_pending(self) -> None:
        while self._queue:
            event = self._queue.pop(0)

            subscribed_handlers = self.handlers_map.get(type(event), [])
            # subscribed_handlers = self._handlers_getter(type(event))

            for handler in subscribed_handlers:
                await handler(event)


def async_event_bus_factory(handlers_map: EventsRegister) -> AsyncInProcessEventBus:
    return AsyncInProcessEventBus(handlers_map=handlers_map)
