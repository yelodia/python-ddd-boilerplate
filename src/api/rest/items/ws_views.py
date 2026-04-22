from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from api.dependencies import WsManagerDep

items_ws_router = APIRouter(prefix="/ws", tags=["items"])


@items_ws_router.websocket("/")
async def websocket_endpoint(ws: WebSocket, mgr: WsManagerDep) -> None:
    await mgr.connect(ws, topic="items")
    try:
        while True:
            data = await ws.receive_text()
            await mgr.broadcast("items", {"message": data})
    except WebSocketDisconnect:
        mgr.disconnect(ws, topic="items")
