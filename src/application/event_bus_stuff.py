from application.event_handler_base import EventHandler
from core.domain_events import DomainEvent

EventType = type[DomainEvent]
EventHandlersRegistry = dict[EventType, list[type[EventHandler]]]
