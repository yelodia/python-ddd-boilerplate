from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from api.dependencies import WsManagerDep

ws_router = APIRouter(prefix="/ws", tags=["websocket"])


@ws_router.websocket("/products")
async def products_ws(websocket: WebSocket, mgr: WsManagerDep) -> None:
    """
    WebSocket-подписка на обновления витрины.

    Клиент получает push-уведомления при изменении любого товара:
      - {"type": "product.stock_changed", "product_id": 1, "pcs_delta": -2}
      - {"type": "product.updated", "product_id": 1, "name": "...", "price": 9.99, ...}
    """
    await mgr.connect(websocket, topic="products")
    try:
        while True:
            await websocket.receive_text()  # keepalive / ping от клиента
    except WebSocketDisconnect:
        mgr.disconnect(websocket, topic="products")


@ws_router.websocket("/carts/{cart_id}")
async def cart_ws(websocket: WebSocket, cart_id: int, mgr: WsManagerDep) -> None:
    """
    WebSocket-подписка на обновления конкретной корзины.

    Клиент получает push-уведомления при изменении состава корзины:
      - {"type": "cart.product_added",   "cart_id": 5, "product_id": 1, "pcs": 2}
      - {"type": "cart.product_removed", "cart_id": 5, "product_id": 1, "pcs": 2}
      - {"type": "cart.cleared",         "cart_id": 5}
    """
    await mgr.connect(websocket, topic=f"cart:{cart_id}")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        mgr.disconnect(websocket, topic=f"cart:{cart_id}")
