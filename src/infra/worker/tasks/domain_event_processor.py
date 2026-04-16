import structlog
from arq.connections import ArqRedis

from infra.event_bus.async_in_arq import AsyncArqEventBus, deserialize_event
from infra.event_handlers_registry import EVENT_HANDLERS
from infra.usecases_builder import UseCasesBuilder

logger = structlog.get_logger(__name__)


async def domain_event_processor(ctx: dict, *, event_key: str, event_data: dict) -> None:
    """
    Универсальный arq-таск для arq-воркеров, которые обрабатывают все задания-события, публикуемые шиной (EventBus).

    Получает из очереди сериализованное событие, реконструирует его в исходный python-объект.
    После, находит все ассоциированные с этим событием хэндлеры и поочерёдно запускает каждый из них
    в том порядке, в котором они были объявлены в регистре для обработки этого события.

    Каждый хэндлер исполняется независимо: ошибка в одном не прерывает остальные.
    Если хэндлер сам публикует события — они уйдут в arq через тот же экземпляр шины.

    ВАЖНОЕ ПРИМЕЧАНИЕ: название этого таска (функции) должно быть известно той реализации шины, которая будет
    конвертировать (сериализовать) DomainEvent'ы в задания для arq-воркеров.
    В противном случае arq-worker просто не поймёт, какой таск ему нужно запускать для обработки этого задания-события.
    """
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(task="domain_event_processor", event_key=event_key)

    arq_client: ArqRedis = ctx['redis']
    bus = AsyncArqEventBus(EVENT_HANDLERS, arq_client)

    if event_key not in bus._index:
        logger.error("Unknown Event, skipping. Please, re-check EVENT_HANDLERS registry.", event_key=event_key)
        return

    event_cls, handler_classes = bus._index[event_key]
    event = deserialize_event(event_cls, event_data)

    # Передаём arq_client в билдер, чтобы хэндлеры получили ту же arq-шину и могли публиковать свои собственные события
    builder = UseCasesBuilder(arq_client=arq_client)
    for handler_cls in handler_classes:
        try:
            handler = builder.build_handler(handler_cls, event_bus=bus)
            await handler.handle(event)
        except Exception:
            logger.exception(
                f"{type(handler_cls)} was failed to process event",
                event_key=event_key,
                handler=handler_cls.__name__,
            )
