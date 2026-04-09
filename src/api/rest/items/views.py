from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from pydantic import BaseModel

from api.dependencies import build
from api.deprecated_dependencies import WsManagerDep
from api.rest.items.responses import ItemResponse
from application.items.commands import (
    CreateItemCmd,
    ShowAllItemsCmd,
    GetItemCmd,
    UpdateItemCmd,
    DeleteItemCmd,
)
from application.items.use_cases import (
    ShowAllItemsUseCase,
    CreateItemUseCase,
    GetItemUseCase,
    UpdateItemUseCase,
    DeleteItemUseCase,
)

router = APIRouter(prefix="/items", tags=["items"])

"""
TODO при добавлении новой сущности:
1) создать сущность в core/*/entities.py
2) создать новый репозиторий (интерфейс) в слое core/BOUNDED_CONTEXT/repository.py
3) создать реализацию репозитория в слое infra/STORAGE_IMPL/repositories/*.py
4) "зарегистрировать" реализации репозиториев в "билдере" infra/usecases_builder.py
5) создать команды и юзкейсы в слое application
6) создать вьюшки и накормить их свежесозданными юзкейсами
"""


@router.get("/", response_model=list[ItemResponse])
async def list_items(
        offset: int = 0,
        limit: int = 10,
        use_case: ShowAllItemsUseCase = build(ShowAllItemsUseCase),
) -> list[ItemResponse]:
    cmd = ShowAllItemsCmd(offset=offset, limit=limit)
    items = await use_case.execute(cmd)
    return [ItemResponse.from_domain(x) for x in items]


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(
        item_id: UUID,
        use_case: GetItemUseCase = build(GetItemUseCase),
) -> ItemResponse:
    cmd = GetItemCmd(item_id=item_id)
    item = await use_case.execute(cmd)
    return ItemResponse.from_domain(item)


@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
        cmd: CreateItemCmd,
        use_case: CreateItemUseCase = build(CreateItemUseCase),
) -> ItemResponse:
    item = await use_case.execute(cmd)
    return ItemResponse.from_domain(item)


class UpdateItemRequestBody(BaseModel):
    title: str
    description: str | None = None

@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(
        item_id: UUID,
        body: UpdateItemRequestBody,
        use_case: UpdateItemUseCase = build(UpdateItemUseCase),
) -> ItemResponse:
    cmd = UpdateItemCmd(item_id=item_id, **body.dict())
    item = await use_case.execute(cmd)
    return ItemResponse.from_domain(item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
        item_id: UUID,
        use_case: DeleteItemUseCase = build(DeleteItemUseCase),
) -> None:
    cmd = DeleteItemCmd(item_id=item_id)
    await use_case.execute(cmd)


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket, mgr: WsManagerDep) -> None:
    await mgr.connect(ws)
    try:
        while True:
            data = await ws.receive_text()
            await mgr.broadcast(f"broadcast: {data}")
    except WebSocketDisconnect:
        mgr.disconnect(ws)
