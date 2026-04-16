import dataclasses
from datetime import datetime
from uuid import UUID

import structlog
from arq.connections import ArqRedis

from application.event_bus_interface import EventBus, EventHandlersRegistry
from core.domain_events import DomainEvent

logger = structlog.get_logger(__name__)

# Имя универсального arq-таска для обработки доменных событий (объявлен в infra/worker/tasks/domain_event_processor.py)
HANDLERS_PROCESSING_TASK_NAME = 'domain_event_processor'

# {строковый путь к классу события: (сам класс, список классов хэндлеров)}
_RegistryIndex = dict[str, tuple[type, list[type]]]


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
    for f in dataclasses.fields(event):
        value = getattr(event, f.name)
        if isinstance(value, UUID):
            value = str(value)
        elif isinstance(value, datetime):
            value = value.isoformat()
        result[f.name] = value
    return result


def deserialize_event(event_cls: type, event_data: dict) -> DomainEvent:
    """
    Реконструирует объект события из словаря.
    Парсит str → UUID и str → datetime обратно, опираясь на аннотации типов класса.
    """
    hints = {f.name: f.type for f in dataclasses.fields(event_cls)}
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

    dispatch_pending() — no-op: задания уже в Redis сразу после каждого publish().

    Цепочки событий работают: хэндлер, получивший этот же экземпляр шины, может вызвать
    publish() — новое задание уйдёт в arq и будет обработано независимо.
    """

    def __init__(self, handlers_registry: EventHandlersRegistry, arq_client: ArqRedis):
        self._arq_client = arq_client
        self._index: _RegistryIndex = _build_index(handlers_registry)

    async def publish(self, event: DomainEvent) -> None:
        event_key = _class_path(type(event))

        if event_key not in self._index:
            logger.warning("arq_event_bus: событие не найдено в регистре, пропускаем", event_key=event_key)
            return

        event_data = serialize_event(event)
        await self._arq_client.enqueue_job(HANDLERS_PROCESSING_TASK_NAME, event_key=event_key, event_data=event_data)
        logger.debug("arq_event_bus: задание поставлено в очередь", event_key=event_key)

    async def dispatch_pending(self) -> None:
        pass  # no-op: задания уже в Redis после каждого publish()
