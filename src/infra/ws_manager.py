from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self._active: list[WebSocket] = []

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self._active.append(ws)

    def disconnect(self, ws: WebSocket) -> None:
        self._active.remove(ws)

    async def broadcast(self, message: str) -> None:
        for ws in self._active:
            await ws.send_text(message)

    async def send_personal(self, message: str, ws: WebSocket) -> None:  # TODO: use for DM/notifications
        await ws.send_text(message)


manager = ConnectionManager()
