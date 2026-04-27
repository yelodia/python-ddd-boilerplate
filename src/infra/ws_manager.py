from collections import defaultdict

import structlog
from fastapi import WebSocket

logger = structlog.get_logger(__name__)


class ConnectionManager:
    """
    Менеджер WebSocket-соединений с маршрутизацией по топикам.

    Топик — строковый ключ, идентифицирующий группу подписчиков:
      - "products"       — все подписчики витрины (broadcast)
      - "cart:{cart_id}" — подписчики конкретной корзины (targeted push)

    Почти что "синглтон": сабж живёт в памяти одного FastAPI-процесса. Для многопроцессного деплоя
    доставка между процессами осуществляется через Redis Pub/Sub (см. infra/ws/pubsub_listener.py).
    """

    def __init__(self) -> None:
        self._connections: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, ws: WebSocket, topic: str) -> None:
        await ws.accept()
        self._connections[topic].add(ws)
        logger.debug("ws: client connected", topic=topic)

    def disconnect(self, ws: WebSocket, topic: str) -> None:
        self._connections[topic].discard(ws)
        logger.debug("ws: client disconnected", topic=topic)

    async def broadcast(self, topic: str, payload: dict) -> None:
        """Отправляет payload всем соединениям в топике. Мёртвые соединения удаляются."""
        dead: set[WebSocket] = set()
        for ws in self._connections.get(topic, set()):
            try:
                await ws.send_json(payload)
            except Exception:
                dead.add(ws)
        for ws in dead:
            self._connections[topic].discard(ws)


ws_manager = ConnectionManager()
