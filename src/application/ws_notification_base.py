from abc import ABC, abstractmethod


# TODO придумать более короткое название для websocket-beacon'ов, "WsNotification" - это прям слишком ту мач
class WsNotification(ABC):
    """
    Намерение уведомить WS-клиентов о некотором факте.

    Не является доменным событием (это внутренняя история) и не является презентационным DTO
    (не знает о HTTP/WS протоколе). Это application-layer контракт: use case или хендлер
    выражают, КОГО и О ЧЁМ уведомить — инфраструктура решает, КАК это доставить.

    topic  — топик для ConnectionManager (без префикса "ws:").
    to_payload() — сериализованный payload для отправки клиенту.
    """

    @property
    @abstractmethod
    def topic(self) -> str: ...

    @abstractmethod
    def to_payload(self) -> dict: ...
