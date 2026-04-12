from typing import Callable

from core.domain_events import DomainEvent

EventType = type[DomainEvent]
EventsRegister = dict[EventType, list[Callable]]

_handlers: EventsRegister = dict()


def on(event_type: EventType) -> Callable:
    """Декоратор для регистрации обработчиков прям на месте их объявления."""

    def decorator(fn: Callable) -> Callable:
        if event_type not in _handlers:
            _handlers[event_type] = []
        _handlers[event_type].append(fn)
        return fn

    return decorator


def get_handlers_for(event_type: EventType) -> list[Callable]:
    return _handlers.get(event_type, [])


def handlers_map_factory() -> EventsRegister:
    h = _handlers
    return h
