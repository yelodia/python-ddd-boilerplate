import structlog

from application.items.commands import (
    ShowAllItemsCmd,
    CreateItemCmd,
    GetItemCmd,
    UpdateItemCmd,
    DeleteItemCmd,
)
from common.use_case_base import UseCase, UowFactory
from core.items.entities import Item
from core.items.repo_interfaces import ItemRepository

logger = structlog.get_logger(__name__)


class ShowAllItemsUseCase(UseCase):
    def __init__(self, repo: ItemRepository):
        self._repo: ItemRepository = repo

    async def execute(self, cmd: ShowAllItemsCmd) -> list[Item]:
        return await self._repo.get_slice(cmd.offset, cmd.limit)


class GetItemUseCase(UseCase):
    def __init__(self, repo: ItemRepository):
        self._repo: ItemRepository = repo

    async def execute(self, cmd: GetItemCmd) -> Item:
        item = await self._repo.get_by_id(cmd.item_id)
        return item


class CreateItemUseCase(UseCase):
    def __init__(self, repo: ItemRepository, uow: UowFactory):
        self._repo: ItemRepository = repo
        self._uow: UowFactory = uow

    async def execute(self, cmd: CreateItemCmd) -> Item:
        new_item = Item(title=cmd.title, description=cmd.description)

        async with self._uow():
            await self._repo.create(new_item)

        return new_item


class UpdateItemUseCase(UseCase):
    def __init__(self, repo: ItemRepository, uow: UowFactory):
        self._repo: ItemRepository = repo
        self._uow: UowFactory = uow

    async def execute(self, cmd: UpdateItemCmd) -> Item:
        async with self._uow():
            item = await self._repo.get_by_id(cmd.item_id)

            item.rename(cmd.title)  # FIXME in cmd at now can be None, but domain entity isn't allow the None value >:(
            item.set_description(cmd.description)

            await self._repo.update(item)

        return item


class DeleteItemUseCase(UseCase):
    def __init__(self, repo: ItemRepository, uow: UowFactory):
        self._repo: ItemRepository = repo
        self._uow: UowFactory = uow

    async def execute(self, cmd: DeleteItemCmd) -> None:
        async with self._uow():
            await self._repo.delete(cmd.item_id)
