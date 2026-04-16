import structlog

from core.shop.events import TheMorningHasCome
from infra.usecases_builder import UseCasesBuilder

logger = structlog.get_logger(__name__)


async def the_morning_has_come_task(ctx: dict) -> None:
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(task="stock_replenishment")

    # да, это событие настолько тупое, что ему даже не нужно сообщать никаких данных
    # сам факт его появления в шине событий - триггерит нужный хэндлер
    event = TheMorningHasCome()

    # можно напрячь целый билдер, чтобы получить ровно ту реализацию шины, которая сейчас повсеместно используется
    builder = UseCasesBuilder(arq_client=ctx["redis"])
    bus = builder.get_event_bus()

    # либо "собрать" шину самостоятельно, ведь нужна-то только она + сам таск всё равно пишется спецом под arq
    # bus = AsyncArqEventBus(EVENT_HANDLERS, arq_client=ctx['redis'])

    await bus.publish(event)
