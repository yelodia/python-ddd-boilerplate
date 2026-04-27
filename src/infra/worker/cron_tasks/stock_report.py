import structlog

from core.shop.events import StockReportRequested
from infra.usecases_builder import UseCasesBuilder

logger = structlog.get_logger(__name__)


async def stock_report_task(ctx: dict) -> None:
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(task="stock_report")

    builder = UseCasesBuilder(arq_client=ctx["redis"])
    await builder.get_event_bus().publish(StockReportRequested())
