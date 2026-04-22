from dataclasses import dataclass
from typing import Self

from application.ws_notification_base import WsNotification
from core.shop.events import CartUpdated, ProductCreated, ProductChanged


@dataclass(frozen=True)
class ProductCreatedWsNotification(WsNotification):
    """Тонкий маяк: на витрине появился новый продукт."""
    product_id: int

    @classmethod
    def from_event(cls, event: ProductCreated) -> Self:
        return cls(product_id=event.product_id)

    @property
    def topic(self) -> str:
        return "products"

    def to_payload(self) -> dict:
        return {"type": "product_created", "product_id": self.product_id}


# TODO возможно, стоит придумать более короткий суффикс websocket-beacon'ов, "WsNotification" - что-то прям ту мач

@dataclass(frozen=True)
class CartChangedWsNotification(WsNotification):
    """Тонкий маяк: состав или состояние корзины изменилось. Клиент сам решает, нужно ли перезапросить."""
    cart_id: int

    @classmethod
    def from_event(cls, event: CartUpdated) -> Self:
        return cls(cart_id=event.cart_id)

    @property
    def topic(self) -> str:
        return f"cart:{self.cart_id}"

    def to_payload(self) -> dict:
        return {"type": "cart_changed", "cart_id": self.cart_id}


# TODO возможно, стоит придумать более короткий суффикс websocket-beacon'ов, "WsNotification" - что-то прям ту мач

@dataclass(frozen=True)
class ProductChangedWsNotification(WsNotification):
    """Тонкий маяк: данные или остаток товара изменились. Клиент сам решает, нужно ли перезапросить."""
    product_id: int

    @classmethod
    def from_event(cls, event: ProductChanged) -> Self:
        return cls(product_id=event.product_id)

    @property
    def topic(self) -> str:
        return "products"

    def to_payload(self) -> dict:
        return {"type": "product_changed", "product_id": self.product_id}
