from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from pydantic import BaseModel

from api.dependencies import ItemUseCasesDep, UowDep, WsManagerDep
from api.rest.items.schemas import ItemCreate, ItemResponse, ItemUpdate
from infra.bootstrap import (
    list_all_items_use_case,
    create_item_use_case,
    get_item_use_case,
    update_item_use_case,
)

router = APIRouter(prefix="/items", tags=["items"])


class ListItemsParams(BaseModel):
    offset: int = 0
    limit: int = 20

@router.get("/", response_model=list[ItemResponse])
async def list_items(offset: int = 0, limit: int = 20) -> list[ItemResponse]:
    items = await list_all_items_use_case().execute(offset=offset, limit=limit)
    return [ItemResponse.from_domain(i) for i in items]


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: UUID) -> ItemResponse:
    item = await get_item_use_case().execute(item_id=item_id)
    return ItemResponse.from_domain(item)


@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(body: ItemCreate) -> ItemResponse:
    item = await create_item_use_case().execute(title=body.title, description=body.description)
    return ItemResponse.from_domain(item)


@router.patch("/{item_id}", response_model=ItemResponse)
async def update_item(item_id: UUID, body: ItemUpdate) -> ItemResponse:
    item = await update_item_use_case().execute(
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
