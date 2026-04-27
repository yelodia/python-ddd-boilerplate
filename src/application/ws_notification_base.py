from abc import ABC, abstractmethod
from typing import Self

from core.domain_events import DomainEvent


# TODO возможно, стоит придумать более короткое название для websocket-beacon'ов, "WsNotification"
class WsNotification(ABC):
    """
    Намерение уведомить WS-клиентов о некотором факте.

    Не является доменным событием (это внутренняя история) и не является презентационным DTO
    (не знает о HTTP/WS протоколе). Это application-layer контракт: шина решает, КОГО и О ЧЁМ
    уведомить (благодаря регистрам WS_EVENTS и EVENT_HANDLERS) — инфраструктура решает, КАК это доставить.
    """

    @classmethod
    @abstractmethod
    def from_event(cls, event: DomainEvent) -> Self:
        """Фабрика: конструирует уведомление из доменного события."""
        raise NotImplementedError

    @property
    @abstractmethod
    def topic(self) -> str:
        """Топик для ConnectionManager (обычная строка, без префикса "ws:")"""
        raise NotImplementedError

    @abstractmethod
    def to_payload(self) -> dict:
        """Сериализатор ws-payload для отправки клиенту."""
        raise NotImplementedError
