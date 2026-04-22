from dataclasses import dataclass

from application.ws_notification_base import WsNotification


# TODO придумать более короткое название для websocket-beacon'ов, "WsNotification" - это прям слишком ту мач

@dataclass(frozen=True)
class CartChangedWsNotification(WsNotification):
    """Тонкий маяк: состав или состояние корзины изменилось. Клиент сам решает, нужно ли перезапросить."""
    cart_id: int

    @property
    def topic(self) -> str:
        return f"cart:{self.cart_id}"

    def to_payload(self) -> dict:
        return {"type": "cart_changed", "cart_id": self.cart_id}


# TODO придумать более короткое название для websocket-beacon'ов, "WsNotification" - это прям слишком ту мач

@dataclass(frozen=True)
class ProductChangedWsNotification(WsNotification):
    """Тонкий маяк: данные или остаток товара изменились. Клиент сам решает, нужно ли перезапросить."""
    product_id: int

    @property
    def topic(self) -> str:
        return "products"

    def to_payload(self) -> dict:
        return {"type": "product_changed", "product_id": self.product_id}
