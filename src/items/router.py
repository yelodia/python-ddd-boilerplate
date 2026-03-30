from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from src.infrastructure.ws_manager import manager
from src.items.dependencies import ItemUseCasesDep
from src.items.schemas import ItemCreate, ItemResponse

router = APIRouter()


@router.get("/", response_model=list[ItemResponse])
async def list_items(
    use_cases: ItemUseCasesDep,
    offset: int = 0,
    limit: int = 20,
) -> list[ItemResponse]:
    return await use_cases.list_items(offset=offset, limit=limit)


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int, use_cases: ItemUseCasesDep) -> ItemResponse:
    return await use_cases.get_item(item_id)


@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(body: ItemCreate, use_cases: ItemUseCasesDep) -> ItemResponse:
    return await use_cases.create_item(body)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int, use_cases: ItemUseCasesDep) -> None:
    await use_cases.delete_item(item_id)


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket) -> None:
    await manager.connect(ws)
    try:
        while True:
            data = await ws.receive_text()
            await manager.broadcast(f"broadcast: {data}")
    except WebSocketDisconnect:
        manager.disconnect(ws)
