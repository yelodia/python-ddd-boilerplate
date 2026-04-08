from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from api.dependencies import WsManagerDep
from api.rest.items.responses import ItemResponse
from application.items.commands import (
    CreateItemCmd,
    ShowAllItemsCmd,
    GetItemCmd,
    UpdateItemCmd,
    DeleteItemCmd,
)
from infra.bootstrap import (
    show_all_items_use_case,
    create_item_use_case,
    get_item_use_case,
    update_item_use_case,
    delete_item_use_case,
)

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=list[ItemResponse])
async def list_items(cmd: ShowAllItemsCmd) -> list[ItemResponse]:
    items = await show_all_items_use_case().execute(cmd)
    return [ItemResponse.from_domain(x) for x in items]


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(cmd: GetItemCmd) -> ItemResponse:
    item = await get_item_use_case().execute(cmd)
    return ItemResponse.from_domain(item)


@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(cmd: CreateItemCmd) -> ItemResponse:
    item = await create_item_use_case().execute(cmd)
    return ItemResponse.from_domain(item)


@router.patch("/{item_id}", response_model=ItemResponse)
async def update_item(cmd: UpdateItemCmd) -> ItemResponse:
    item = await update_item_use_case().execute(cmd)
    return ItemResponse.from_domain(item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(cmd: DeleteItemCmd) -> None:
    await delete_item_use_case().execute(cmd)


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket, mgr: WsManagerDep) -> None:
    await mgr.connect(ws)
    try:
        while True:
            data = await ws.receive_text()
            await mgr.broadcast(f"broadcast: {data}")
    except WebSocketDisconnect:
        mgr.disconnect(ws)
