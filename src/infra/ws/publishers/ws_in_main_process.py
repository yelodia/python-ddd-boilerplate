from application.ws_notification_base import WsNotification
from application.ws_publisher_interface import WsPublisher
from infra.ws_manager import ConnectionManager


class InProcessWsPublisher(WsPublisher):
    """
    Реализация WsPublisher для FastAPI-процесса.

    Вызывает ConnectionManager.broadcast() напрямую — никакого Redis, никаких переходов
    между процессами. Используется use cases и handlers, выполняющимися в рамках
    HTTP-запроса (т.е. в том же процессе, что и WebSocket-соединения).
    """

    def __init__(self, ws_manager: ConnectionManager) -> None:
        self._manager = ws_manager

    async def notify(self, notification: WsNotification) -> None:
        await self._manager.broadcast(notification.topic, notification.to_payload())
