import structlog
from arq.connections import ArqRedis

from infra.event_bus.async_in_arq import AsyncArqEventBus, deserialize_event
from infra.event_handlers_registry import EVENT_HANDLERS
from infra.usecases_builder import UseCasesBuilder

logger = structlog.get_logger(__name__)


async def dispatch_event(ctx: dict, *, event_key: str, event_data: dict) -> None:
    """
    Универсальный arq-таск-диспетчер.

    Получает из очереди сериализованное событие, реконструирует его, находит все
    зарегистрированные хэндлеры и поочерёдно запускает каждый из них.

    Каждый хэндлер исполняется независимо: ошибка в одном не прерывает остальные.
    Если хэндлер сам публикует события — они уйдут в arq через тот же экземпляр шины.
    """
    arq_client: ArqRedis = ctx['redis']
    bus = AsyncArqEventBus(EVENT_HANDLERS, arq_client)

    if event_key not in bus._index:
        logger.error("dispatch_event: неизвестное событие, нет в регистре", event_key=event_key)
        return

    event_cls, handler_classes = bus._index[event_key]
    event = deserialize_event(event_cls, event_data)

    # Передаём arq_client в билдер — хэндлеры получат ту же arq-шину
    # и смогут публиковать свои события тоже через arq (цепочки событий работают).
    builder = UseCasesBuilder(arq_client=arq_client)
    for handler_cls in handler_classes:
        try:
            handler = builder.build_handler(handler_cls, event_bus=bus)
            await handler.handle(event)
        except Exception:
            logger.exception(
                "dispatch_event: хэндлер завершился с ошибкой",
                event_key=event_key,
                handler=handler_cls.__name__,
            )
