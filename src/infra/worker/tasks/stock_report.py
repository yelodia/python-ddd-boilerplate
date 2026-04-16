import structlog

from core.shop.repo_interfaces import ProductRepository
from infra.usecases_builder import UseCasesBuilder

logger = structlog.get_logger(__name__)

LOW_STOCK_THRESHOLD = 5  # товары с остатком ≤ этого значения считаются "мало на полке"


async def stock_report_task(ctx: dict) -> None:  # FIXME non-DDD implementation!
    """
    Обходит все товары и логирует те, у которых остаток на полке опустился ниже порогового значения.
    Ничего не меняет — только читает и сигнализирует.
    """
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(task="stock_report")

    builder = UseCasesBuilder()
    repo = builder.get_entity_repo(ProductRepository)

    low_stock = []
    offset = 0
    limit = 100

    while True:
        batch = await repo.get_slice(offset=offset, limit=limit)
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

    logger.warning("обнаружены товары с низким остатком", count=len(low_stock))
    for product in low_stock:
        logger.warning(
            "низкий остаток",
            product_id=product.id,
            name=product.name,
            stock=product.stock,
            threshold=LOW_STOCK_THRESHOLD,
        )
