from abc import ABC, abstractmethod

from application.ws_notification_base import WsNotification


class WsPublisher(ABC):
    """
    Абстракция для доставки WS-уведомлений клиентам.

    Принимает WsNotification — application-layer объект с явным topic и payload.

    Конкретная реализация WsPublisher решает, как доставить:
    - напрямую через ConnectionManager (InProcessWsPublisher, для FastAPI-процесса);
    - или через Redis Pub/Sub (RedisWsPublisher, для arq-воркеров).
    """

    @abstractmethod
    async def notify(self, notification: WsNotification) -> None: ...
