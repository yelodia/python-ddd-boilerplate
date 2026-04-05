from typing import Type

import structlog

from common.use_case_base import UseCase
from core.items.repository import ItemRepository
from infrastructure.database.repositories.items import user_repository_factory
from infrastructure.database.uow import UnitOfWork, unit_of_work
from src.core.items.entities import Item
from src.core.items.service import ItemService

logger = structlog.get_logger(__name__)


class ItemUseCases:
    _repo = UserRepo(sdbfsjkdhflk)


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


class CreateItemUseCase(UseCase):
    def __init__(self, repo_factory, session):
        self._repo_factory = repo_factory
        self._session = session

    async def execute(self, title: str, description: str | None = None) -> Item:
        async with unit_of_work(self._session) as uow:
            repo = self._repo_factory(uow.session)
            new_item = await repo.create(title=title, description=description)

            return new_item


create_item_use_case = CreateItemUseCase(item_repository_factory, get_uow)
