import structlog

from application.event_bus_stuff import on
from core.shop.events import (
    NewCartCreated,
    ProductWasAddedToCart,
    ProductWasRemovedFromCart,
    CartWasCleared,
)

logger = structlog.get_logger(__name__)


@on(NewCartCreated)
async def new_cart_created_handler(event: NewCartCreated) -> None:
    logger.debug(event)


@on(ProductWasAddedToCart)
async def product_was_added_to_cart_handler(event: ProductWasAddedToCart) -> None:
    logger.debug(event)


@on(ProductWasRemovedFromCart)
async def product_was_removed_from_cart_handler(event: ProductWasRemovedFromCart) -> None:
    logger.debug(event)


@on(CartWasCleared)
async def cart_was_cleared_handler(event: CartWasCleared) -> None:
    logger.debug(event)
