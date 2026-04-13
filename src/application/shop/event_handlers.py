import structlog

from application.event_handler_base import EventHandler
from application.use_case_base import UowFactory
from core.shop.events import (
    NewCartCreated,
    ProductWasAddedToCart,
    ProductWasRemovedFromCart,
    CartWasCleared,
    ProductWasTakenFromShelf,
    ProductWasReturnedToShelf,
)
from core.shop.repo_interfaces import ProductRepository

logger = structlog.get_logger(__name__)


class NewCartCreatedHandler(EventHandler):
    async def handle(self, event: NewCartCreated) -> None:
        logger.debug(event)


class ProductWasAddedToCartHandler(EventHandler):
    """Уменьшает остаток товара на полке, когда покупатель кладёт его в корзину."""

    def __init__(self, repo: ProductRepository, uow: UowFactory):
        self._repo = repo
        self._uow = uow

    async def handle(self, event: ProductWasAddedToCart) -> None:
        async with self._uow():
            product = await self._repo.get_by_id(event.product_id)
            product.take_from_shelf(event.pcs)
            await self._repo.update(product)

        logger.debug(event)


class ProductWasRemovedFromCartHandler(EventHandler):
    """Возвращает товар на полку, когда покупатель убирает его из корзины."""

    def __init__(self, repo: ProductRepository, uow: UowFactory):
        self._repo = repo
        self._uow = uow

    async def handle(self, event: ProductWasRemovedFromCart) -> None:
        async with self._uow():
            product = await self._repo.get_by_id(event.product_id)
            product.return_to_shelf(event.pcs)
            await self._repo.update(product)

        logger.debug(event)


class CartWasClearedHandler(EventHandler):
    async def handle(self, event: CartWasCleared) -> None:
        logger.debug(event)


class ProductShelfEventHandler(EventHandler):
    """Логирует события изменения остатков товара на полке."""

    async def handle(self, event: ProductWasTakenFromShelf | ProductWasReturnedToShelf) -> None:
        logger.debug(event)
