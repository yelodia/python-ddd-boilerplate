from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from src.api.dependencies import ItemUseCasesDep, UowDep, WsManagerDep
from src.api.rest.items.schemas import ItemCreate, ItemResponse, ItemUpdate

router = APIRouter()


@router.get("/", response_model=list[ItemResponse])
async def list_items(
    use_cases: ItemUseCasesDep,
    offset: int = 0,
    limit: int = 20,
) -> list[ItemResponse]:
    items = await use_cases.list_items(offset=offset, limit=limit)
    return [ItemResponse.from_domain(i) for i in items]


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int, use_cases: ItemUseCasesDep) -> ItemResponse:
    item = await use_cases.get_item(item_id)
    return ItemResponse.from_domain(item)


@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    body: ItemCreate,
    use_cases: ItemUseCasesDep,
    _uow: UowDep,
) -> ItemResponse:
    item = await use_cases.create_item(title=body.title, description=body.description)
    return ItemResponse.from_domain(item)


@router.patch("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: int,
    body: ItemUpdate,
    use_cases: ItemUseCasesDep,
    _uow: UowDep,
) -> ItemResponse:
    item = await use_cases.update_item(
        item_id,
        title=body.title,
        description=body.description,
    )
    return ItemResponse.from_domain(item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int,
    use_cases: ItemUseCasesDep,
    _uow: UowDep,
) -> None:
    await use_cases.delete_item(item_id)


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket, mgr: WsManagerDep) -> None:
    await mgr.connect(ws)
    try:
        while True:
            data = await ws.receive_text()
            await mgr.broadcast(f"broadcast: {data}")
    except WebSocketDisconnect:
        mgr.disconnect(ws)
