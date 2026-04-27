import json

import structlog
from redis.asyncio import Redis

from infra.ws_manager import ConnectionManager

logger = structlog.get_logger(__name__)


async def ws_pubsub_listener(manager: ConnectionManager, redis: Redis) -> None:
    """
    Фоновая задача FastAPI: слушает Redis Pub/Sub и доставляет сообщения WebSocket-клиентам.

    Схема:
        arq Worker → redis.publish("ws:products" | "ws:cart:{id}", JSON)
            → эта функция получает сообщение
            → ConnectionManager.broadcast(topic, payload)
            → WebSocket.send_json() → клиент

    Подписки:
        "ws:products"  — точный канал для обновлений витрины
        "ws:cart:*"    — паттерн для всех корзин (psubscribe)

    Запускается в lifespan FastAPI как asyncio.create_task().
    """
    pubsub = redis.pubsub()
    await pubsub.subscribe("ws:products")
    await pubsub.psubscribe("ws:cart:*")
    logger.info("ws pubsub listener started")

    try:
        async for message in pubsub.listen():
            msg_type = message.get("type")
            if msg_type not in ("message", "pmessage"):
                continue

            try:
                # channel приходит как bytes
                raw_channel: bytes = message["channel"]
                channel = raw_channel.decode()
                # "ws:products" → "products", "ws:cart:42" → "cart:42"
                topic = channel.removeprefix("ws:")
                payload = json.loads(message["data"])
                await manager.broadcast(topic, payload)
            except Exception:
                logger.exception("ws pubsub listener: error processing message", message=message)
    finally:
        await pubsub.unsubscribe("ws:products")
        await pubsub.punsubscribe("ws:cart:*")
        await pubsub.aclose()
        logger.info("ws pubsub listener stopped")
