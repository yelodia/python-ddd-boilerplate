import structlog

from application.event_handler_base import EventHandler
from core.shop.events import (
    NewCartCreated,
    ProductWasAddedToCart,
    ProductWasRemovedFromCart,
    CartWasCleared,
)

logger = structlog.get_logger(__name__)


class NewCartCreatedHandler(EventHandler):
    async def handle(self, event: NewCartCreated) -> None:
        logger.debug(event)


class ProductWasAddedToCartHandler(EventHandler):
    async def handle(self, event: ProductWasAddedToCart) -> None:
        logger.debug(event)


class ProductWasRemovedFromCartHandler(EventHandler):
    async def handle(self, event: ProductWasRemovedFromCart) -> None:
        logger.debug(event)


class CartWasClearedHandler(EventHandler):
    async def handle(self, event: CartWasCleared) -> None:
        logger.debug(event)
