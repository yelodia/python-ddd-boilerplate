import structlog

from core.shop.repo_interfaces import ProductRepository
from infra.usecases_builder import UseCasesBuilder

logger = structlog.get_logger(__name__)

LOW_STOCK_THRESHOLD = 5  # порог, ниже которого товар считается требующим пополнения
REPLENISHMENT_TARGET = 20  # до какого значения пополняем остаток


async def stock_replenishment_task(ctx: dict) -> None:
    """
    Обходит все товары и пополняет остаток тех, у кого он опустился ниже порогового значения.
    Каждый товар обновляется в отдельной транзакции — чтобы ошибка по одному не откатила остальные.
    """
    builder = UseCasesBuilder()
    repo = builder.get_entity_repo(ProductRepository)

    replenished = []
    failed = []
    offset = 0
    limit = 100

    while True:
        batch = await repo.get_slice(offset=offset, limit=limit)
        if not batch:
            break

        for product in batch:
            if product.stock >= LOW_STOCK_THRESHOLD:
                continue

            amount = REPLENISHMENT_TARGET - product.stock
            try:
                async with builder.get_uow():
                    product.return_to_shelf(amount)
                    await repo.update(product)
                replenished.append((product.id, product.name, product.stock))
            except Exception:
                logger.exception(
                    "stock_replenishment: не удалось пополнить товар",
                    product_id=product.id,
                    name=product.name,
                )
                failed.append(product.id)

        if len(batch) < limit:
            break
        offset += limit

    if replenished:
        logger.info("stock_replenishment: пополнение завершено", count=len(replenished))
        for product_id, name, stock_after in replenished:
            logger.info(
                "stock_replenishment: пополнен",
                product_id=product_id,
                name=name,
                stock_after=stock_after,
            )

    if failed:
        logger.error("stock_replenishment: часть товаров не удалось пополнить", failed_ids=failed)

    if not replenished and not failed:
        logger.info("stock_replenishment: нечего пополнять, все остатки выше порога", threshold=LOW_STOCK_THRESHOLD)
