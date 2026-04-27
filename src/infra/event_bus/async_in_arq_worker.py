from dataclasses import fields as dataclass_fields
from datetime import datetime
from uuid import UUID

import structlog
from arq.connections import ArqRedis

from application.event_bus_interface import EventBus, EventHandlersRegistry
from application.event_handler_base import EventHandler
from application.ws_publisher_interface import WsPublisher
from core.domain_events import DomainEvent
from infra.ws_events_registry import WsEventsRegistry

logger = structlog.get_logger(__name__)

# Имя универсального arq-таска для обработки доменных событий (объявлен в infra/worker/tasks/domain_event_processor.py)
HANDLERS_PROCESSING_TASK_NAME = 'domain_event_processor'

# {строковый путь к классу события: (сам класс, список классов хэндлеров)}
_RegistryIndex = dict[str, tuple[type[DomainEvent], list[type[EventHandler]]]]


def _class_path(cls: type) -> str:
    """Возвращает полный путь к классу в виде строки: 'module.ClassName'."""
    return f"{cls.__module__}.{cls.__qualname__}"


def _build_index(registry: EventHandlersRegistry) -> _RegistryIndex:
    """
    Конвертирует регистр из {EventClass: [HandlerClass, ...]}
    в {строковый_путь_события: (EventClass, [HandlerClass, ...])}.

    Строковый ключ нужен, чтобы воркер мог идентифицировать событие по данным из arq-задания,
    не прибегая к динамическому импорту в горячем пути — все классы уже загружены при старте.
    """
    return {
        _class_path(event_cls): (event_cls, handler_classes)
        for event_cls, handler_classes in registry.items()
    }


def serialize_event(event: DomainEvent) -> dict:
    """
    Сериализует все поля события в JSON-совместимый словарь.
    UUID → str, datetime → ISO-строка, остальное — как есть.
    """
    result = {}
    for f in dataclass_fields(event):
        value = getattr(event, f.name)
        if isinstance(value, UUID):
            value = str(value)
        elif isinstance(value, datetime):
            value = value.isoformat()
        result[f.name] = value
    return result


def deserialize_event(event_cls: type[DomainEvent], event_data: dict) -> DomainEvent:
    """
    Реконструирует объект события из словаря.
    Парсит str → UUID и str → datetime обратно, опираясь на аннотации типов класса.
    """
    hints = {f.name: f.type for f in dataclass_fields(event_cls)}
    kwargs = {}
    for key, value in event_data.items():
        annotation = hints.get(key)
        if annotation is UUID or annotation == 'UUID':
            value = UUID(value)
        elif annotation is datetime or annotation == 'datetime':
            value = datetime.fromisoformat(value)
        kwargs[key] = value
    return event_cls(**kwargs)


class AsyncArqEventBus(EventBus):
    """
    Реализация EventBus на базе arq (Redis-очередь).

    При publish() сериализует событие и ставит одно задание в arq-очередь.
    Воркер подхватывает его, реконструирует событие и прогоняет через все зарегистрированные
    хэндлеры — используя тот же регистр и тот же индекс.

    Каждый publish() немедленно ставит задание в Redis — никакой буферизации нет.

    Цепочки событий работают: хэндлер, получивший этот же экземпляр шины, может вызвать
    publish() — новое задание уйдёт в arq и будет обработано независимо.
    """

    def __init__(
            self,
            handlers_registry: EventHandlersRegistry,
            arq_client: ArqRedis,
            ws_events_registry: WsEventsRegistry,
            ws_publisher: WsPublisher,
    ):
        self._arq_client = arq_client
        self._index: _RegistryIndex = _build_index(handlers_registry)
        self._ws_events_registry = ws_events_registry
        self._ws_publisher = ws_publisher

    async def publish(self, event: DomainEvent) -> None:
        # WS первым - он лёгкий, не требует сериализации и round-trip до Redis, потом всё остальное
        await self._notify_ws_subscribers(event)
        await self._enqueue_handlers(event)

    async def _notify_ws_subscribers(self, event: DomainEvent) -> None:
        notification_cls = self._ws_events_registry.get(type(event), None)
        if notification_cls is None:
            return
        notification = notification_cls.from_event(event)
        await self._ws_publisher.notify(notification)

    async def _enqueue_handlers(self, event: DomainEvent) -> None:
        event_key = _class_path(type(event))
        if event_key not in self._index:
            return
        event_data = serialize_event(event)
        await self._arq_client.enqueue_job(HANDLERS_PROCESSING_TASK_NAME, event_key=event_key, event_data=event_data)
        logger.debug("Job queued", event_key=event_key)
