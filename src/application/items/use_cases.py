from uuid import UUID

import structlog

from application.uow import UnitOfWork
from common.use_case_base import UseCase
from core.items.entities import Item
from core.items.repository import ItemRepository
from core.items.service import ItemService

logger = structlog.get_logger(__name__)


class ItemUseCases:
    def __init__(self, service: ItemService) -> None:
        self.service = service

    async def get_item(self, item_id: int) -> Item:
        return await self.service.get_item(item_id)

    async def list_items(self, offset: int, limit: int) -> list[Item]:
        return await self.service.list_items(offset, limit)

    async def create_item(self, title: str, description: str | None = None) -> Item:
        item = await self.service.create_item(title=title, description=description)
        logger.info("item_created", item_id=item.id, title=item.title)
        return item

    async def update_item(
        self, item_id: int, title: str | None = None, description: str | None = ...
    ) -> Item:
        item = await self.service.update_item(item_id, title=title, description=description)
        logger.info("item_updated", item_id=item.id)
        return item

    async def delete_item(self, item_id: int) -> None:
        await self.service.delete_item(item_id)
        logger.info("item_deleted", item_id=item_id)


class ListAllItemsUseCase(UseCase):
    def __init__(self, repo):
        self._repo: ItemRepository = repo

    async def execute(self, offset: int, limit: int) -> list[Item]:
        return await self._repo.get_all(offset, limit)


class GetItemUseCase(UseCase):
    def __init__(self, repo):
        self._repo: ItemRepository = repo

    async def execute(self, item_id: UUID) -> Item:
        return await self._repo.get_by_id(item_id)


class CreateItemUseCase(UseCase):
    def __init__(self, repo: ItemRepository, uow: UnitOfWork):
        self._repo: ItemRepository = repo
        self._uow: UnitOfWork = uow

    async def execute(self, title: str, description: str | None = None) -> Item:
        new_item = Item(title=title, description=description)

        async with self._uow as uow:
            await self._repo.create(new_item)
            await uow.commit()

        return new_item

