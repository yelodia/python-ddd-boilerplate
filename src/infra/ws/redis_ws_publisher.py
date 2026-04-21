import json

from arq.connections import ArqRedis

from application.ws_publisher_interface import WsPublisher


class RedisWsPublisher(WsPublisher):
    """
    Реализация WsPublisher через Redis Pub/Sub.

    Публикует JSON-payload в указанный канал. FastAPI-процессы слушают эти каналы
    через pubsub_listener и доставляют сообщения подключённым WebSocket-клиентам.

    ArqRedis расширяет aioredis.Redis, поэтому поддерживает publish() напрямую —
    отдельный Redis-клиент для Pub/Sub не нужен.
    """

    def __init__(self, redis: ArqRedis) -> None:
        self._redis = redis

    async def publish(self, channel: str, payload: dict) -> None:
        await self._redis.publish(channel, json.dumps(payload))
