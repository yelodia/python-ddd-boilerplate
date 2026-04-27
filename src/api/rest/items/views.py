from uuid import UUID

from fastapi import APIRouter, status
from pydantic import BaseModel

from api.dependencies import build
from api.rest.items.responses import ItemResponse
from application.items.use_cases import (
    ShowAllItemsUseCase,
    CreateItemUseCase,
    GetItemUseCase,
    UpdateItemUseCase,
    DeleteItemUseCase,
)

items_router = APIRouter(prefix="/items", tags=["items"])

"""
TODO при добавлении новой сущности:
1) создать сущность в core/*/entities.py
2) создать новый репозиторий (интерфейс) в слое core/BOUNDED_CONTEXT/repo_interfaces.py
3) создать реализацию репозитория в слое infra/STORAGE_IMPL/repositories/*.py
4) "зарегистрировать" реализации репозиториев в "билдере" infra/usecases_builder.py
5) создать команды и юзкейсы в слое application
6) создать вьюшки и накормить их свежесозданными юзкейсами
"""


@items_router.get("/", response_model=list[ItemResponse])
async def list_items(
        offset: int = 0,
        limit: int = 10,
        use_case: ShowAllItemsUseCase = build(ShowAllItemsUseCase),
) -> list[ItemResponse]:
    cmd = use_case.cmd(offset=offset, limit=limit)
    items = await use_case.execute(cmd)
    return [ItemResponse.from_domain(x) for x in items]


@items_router.get("/{item_id}", response_model=ItemResponse)
async def get_item(
        item_id: UUID,
        use_case: GetItemUseCase = build(GetItemUseCase),
) -> ItemResponse:
    cmd = use_case.cmd(item_id=item_id)
    item = await use_case.execute(cmd)
    return ItemResponse.from_domain(item)


class CreateItemRequest(BaseModel):
    title: str
    description: str | None = None


@items_router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
        body: CreateItemRequest,
        use_case: CreateItemUseCase = build(CreateItemUseCase),
) -> ItemResponse:
    cmd = use_case.cmd(title=body.title, description=body.description)
    item = await use_case.execute(cmd)
    return ItemResponse.from_domain(item)


class UpdateItemRequestBody(BaseModel):
    title: str
    description: str | None = None


@items_router.put("/{item_id}", response_model=ItemResponse)
async def update_item(
        item_id: UUID,
        body: UpdateItemRequestBody,
        use_case: UpdateItemUseCase = build(UpdateItemUseCase),
) -> ItemResponse:
    cmd = use_case.cmd(item_id=item_id, title=body.title, description=body.description)
    item = await use_case.execute(cmd)
    return ItemResponse.from_domain(item)


@items_router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
        item_id: UUID,
        use_case: DeleteItemUseCase = build(DeleteItemUseCase),
) -> None:
    cmd = use_case.cmd(item_id=item_id)
    await use_case.execute(cmd)
