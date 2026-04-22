import structlog

from application.event_bus_interface import EventBus
from application.event_handler_base import EventHandler
from application.use_case_base import UowFactory
from core.shop.events import (
    NewCartCreated,
    ProductWasAddedToCart,
    ProductWasRemovedFromCart,
    CartWasCleared,
    ProductWasTakenFromShelf,
    ProductWasReturnedToShelf,
    TheMorningHasCome,
)
from core.shop.repo_interfaces import ProductRepository

logger = structlog.get_logger(__name__)


class NewCartCreatedHandler(EventHandler):
    async def handle(self, event: NewCartCreated) -> None:
        logger.debug(event)


class ProductWasAddedToCartHandler(EventHandler):
    """Наблюдательный хендлер: фиксирует факт добавления товара в корзину (метрики, логи).
    Остаток на полке уменьшается синхронно в PutProductToCartUseCase — не здесь."""

    async def handle(self, event: ProductWasAddedToCart) -> None:
        logger.debug(event)


class ProductWasRemovedFromCartHandler(EventHandler):
    """Возвращает товар на полку, когда покупатель убирает его из корзины."""

    def __init__(self, repo: ProductRepository, uow: UowFactory, event_bus: EventBus):
        self._repo = repo
        self._uow = uow
        self._event_bus = event_bus

    async def handle(self, event: ProductWasRemovedFromCart) -> None:
        async with self._uow():
            product = await self._repo.get_by_id(event.product_id)
            product.return_to_shelf(event.pcs)
            await self._repo.update(product)

        for product_event in product._events:
            await self._event_bus.publish(product_event)

        logger.debug(event)


class CartWasClearedHandler(EventHandler):
    async def handle(self, event: CartWasCleared) -> None:
        logger.debug(event)


class ProductShelfEventHandler(EventHandler):
    """Логирует события изменения остатков товара на полке."""

    async def handle(self, event: ProductWasTakenFromShelf | ProductWasReturnedToShelf) -> None:
        logger.debug(event)


LOW_STOCK_THRESHOLD = 5  # порог, ниже которого товар считается требующим пополнения
REPLENISHMENT_TARGET = 20  # до какого значения пополняем остаток


class StockReplenishmentRequestedHandler(EventHandler):
    """Пополняет остатки всех товаров, упавших ниже порогового значения."""

    def __init__(self, repo: ProductRepository, uow: UowFactory, event_bus: EventBus):
        self._repo = repo
        self._uow = uow
        self._event_bus = event_bus

    async def handle(self, event: TheMorningHasCome) -> None:
        replenished = []
        failed = []
        offset = 0
        limit = 100

        while True:
            batch = await self._repo.get_slice(offset=offset, limit=limit)
            if not batch:
                break

            for product in batch:
                if product.stock >= LOW_STOCK_THRESHOLD:
                    continue

                try:
                    async with self._uow():
                        product.stock_replenishment(REPLENISHMENT_TARGET)
                        await self._repo.update(product)

                    for product_event in product._events:
                        await self._event_bus.publish(product_event)

                    replenished.append((product.id, product.name, product.stock))
                except Exception:
                    logger.exception(
                        "не удалось пополнить товар",
                        product_id=product.id,
                        name=product.name,
                    )
                    failed.append(product.id)

            if len(batch) < limit:
                break
            offset += limit

        if replenished:
            logger.info("пополнение завершено", count=len(replenished))
            for product_id, name, stock_after in replenished:
                logger.info("пополнен", product_id=product_id, name=name, stock_after=stock_after)

        if failed:
            logger.error("часть товаров не удалось пополнить", failed_ids=failed)

        if not replenished and not failed:
            logger.info("нечего пополнять, все остатки выше порога", threshold=LOW_STOCK_THRESHOLD)
