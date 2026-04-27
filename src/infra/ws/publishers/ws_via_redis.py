import json

from arq.connections import ArqRedis

from application.ws_notification_base import WsNotification
from application.ws_publisher_interface import WsPublisher


class RedisWsPublisher(WsPublisher):
    """
    Реализация WsPublisher для arq-воркеров.

    Публикует payload в Redis Pub/Sub канал "ws:{topic}". FastAPI-процесс слушает эти каналы
    через pubsub_listener и доставляет сообщения подключённым WebSocket-клиентам.

    ArqRedis расширяет aioredis.Redis, поэтому поддерживает publish() напрямую —
    отдельный Redis-клиент для Pub/Sub не нужен.
    """

    def __init__(self, redis: ArqRedis) -> None:
        self._redis = redis

    async def notify(self, notification: WsNotification) -> None:
        channel = f"ws:{notification.topic}"
        await self._redis.publish(channel, json.dumps(notification.to_payload()))
