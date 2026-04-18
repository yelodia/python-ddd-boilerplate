import structlog

from application.event_handler_base import EventHandler
from application.reports.report_storage import ReportStorage
from core.shop.events import StockReportRequested
from core.shop.repo_interfaces import ProductRepository

logger = structlog.get_logger(__name__)

LOW_STOCK_THRESHOLD = 5  # товары с остатком ≤ этого значения считаются "мало на полке"


class StockReportRequestedHandler(EventHandler):
    """Обходит все товары, собирает те, у которых остаток ниже порога, и сохраняет отчёт в CSV."""

    def __init__(self, repo: ProductRepository, storage: ReportStorage):
        self.repo = repo
        self.storage = storage

    async def handle(self, event: StockReportRequested) -> None:
        low_stock = []
        offset = 0
        limit = 100

        while True:
            batch = await self.repo.get_slice(offset=offset, limit=limit)
            if not batch:
                break
            for product in batch:
                if product.stock <= LOW_STOCK_THRESHOLD:
                    low_stock.append(product)
            if len(batch) < limit:
                break
            offset += limit

        if not low_stock:
            logger.info("все товары в норме, остатки выше порога", threshold=LOW_STOCK_THRESHOLD)
            return

        rows = [
            {"product_id": p.id, "name": p.name, "stock": p.stock, "threshold": LOW_STOCK_THRESHOLD}
            for p in low_stock
        ]
        filename = f"stock_report_{event.occurred_at.strftime('%Y-%m-%dT%H-%M-%S')}.csv"
        self.storage.save(filename, rows, fieldnames=["product_id", "name", "stock", "threshold"])

        logger.warning(
            "обнаружены товары с низким остатком, отчёт сохранён",
            count=len(low_stock),
            file=filename,
        )
