from abc import ABC, abstractmethod


class WsPublisher(ABC):
    """
    Абстракция для публикации уведомлений в WebSocket-слой.

    Позволяет хендлерам (application layer) отправлять push-уведомления клиентам,
    не зная ничего о конкретном транспорте (Redis Pub/Sub, in-process очередь и т.п.).
    """

    @abstractmethod
    async def publish(self, channel: str, payload: dict) -> None: ...
