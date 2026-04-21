from application.event_handler_base import EventHandler
from application.ws_publisher_interface import WsPublisher
from core.domain_events import DomainEvent
from core.shop.events import (
    ProductWasTakenFromShelf,
    ProductWasReturnedToShelf,
    ProductUpdated,
    ProductCreated,
    ProductWasAddedToCart,
    ProductWasRemovedFromCart,
    CartWasCleared,
)

PRODUCTS_CHANNEL = "ws:products"


class ProductStockWsNotifier(EventHandler):
    """
    Уведомляет подписчиков /ws/products об изменении остатка конкретного товара.
    Срабатывает на ProductWasTakenFromShelf и ProductWasReturnedToShelf.
    """

    def __init__(self, ws_publisher: WsPublisher) -> None:
        self._publisher = ws_publisher

    async def handle(self, event: DomainEvent) -> None:
        assert isinstance(event, (ProductWasTakenFromShelf, ProductWasReturnedToShelf))
        await self._publisher.publish(PRODUCTS_CHANNEL, {
            "type": "product.stock_changed",
            "product_id": event.product_id,
            "pcs_delta": -event.pcs if isinstance(event, ProductWasTakenFromShelf) else event.pcs,
        })


class ProductCreatedWsNotifier(EventHandler):
    """
    Уведомляет подписчиков /ws/products о появлении нового товара.
    Срабатывает на ProductCreated.
    """

    def __init__(self, ws_publisher: WsPublisher) -> None:
        self._publisher = ws_publisher

    async def handle(self, event: DomainEvent) -> None:
        assert isinstance(event, ProductCreated)
        await self._publisher.publish(PRODUCTS_CHANNEL, {
            "type": "product.created",
            "product_id": event.product_id,
            "name": event.name,
            "price": event.price,
            "description": event.description,
            "stock": event.stock,
        })


class ProductInfoWsNotifier(EventHandler):
    """
    Уведомляет подписчиков /ws/products об изменении данных товара (цена, название, описание).
    Срабатывает на ProductUpdated.
    """

    def __init__(self, ws_publisher: WsPublisher) -> None:
        self._publisher = ws_publisher

    async def handle(self, event: DomainEvent) -> None:
        assert isinstance(event, ProductUpdated)
        await self._publisher.publish(PRODUCTS_CHANNEL, {
            "type": "product.updated",
            "product_id": event.product_id,
            "name": event.name,
            "price": event.price,
            "description": event.description,
            "stock": event.stock,
        })


class CartWsNotifier(EventHandler):
    """
    Уведомляет подписчиков /ws/carts/{cart_id} об изменениях внутри корзины.
    Срабатывает на ProductWasAddedToCart, ProductWasRemovedFromCart, CartWasCleared.
    """

    def __init__(self, ws_publisher: WsPublisher) -> None:
        self._publisher = ws_publisher

    async def handle(self, event: DomainEvent) -> None:
        assert isinstance(event, (ProductWasAddedToCart, ProductWasRemovedFromCart, CartWasCleared))

        if isinstance(event, ProductWasAddedToCart):
            payload = {
                "type": "cart.product_added",
                "cart_id": event.cart_id,
                "product_id": event.product_id,
                "pcs": event.pcs,
            }
        elif isinstance(event, ProductWasRemovedFromCart):
            payload = {
                "type": "cart.product_removed",
                "cart_id": event.cart_id,
                "product_id": event.product_id,
                "pcs": event.pcs,
            }
        else:
            payload = {
                "type": "cart.cleared",
                "cart_id": event.cart_id,
            }

        await self._publisher.publish(f"ws:cart:{event.cart_id}", payload)
