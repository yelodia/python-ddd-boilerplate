import structlog

from application.items.commands import (
    ShowAllItemsCmd,
    CreateItemCmd,
    GetItemCmd,
    UpdateItemCmd,
    DeleteItemCmd,
)
from application.use_case_base import UseCase, UowFactory
from core.items.entities import Item
from core.items.repo_interfaces import ItemRepository

logger = structlog.get_logger(__name__)


class ShowAllItemsUseCase(UseCase):
    def __init__(self, repo: ItemRepository):
        self.repo = repo

    async def execute(self, cmd: ShowAllItemsCmd) -> list[Item]:
        return await self.repo.get_slice(cmd.offset, cmd.limit)


class GetItemUseCase(UseCase):
    def __init__(self, repo: ItemRepository):
        self.repo = repo

    async def execute(self, cmd: GetItemCmd) -> Item:
        item = await self.repo.get_by_id(cmd.item_id)
        return item


class CreateItemUseCase(UseCase):
    def __init__(self, repo: ItemRepository, uow: UowFactory):
        self.repo = repo
        self.uow = uow

    async def execute(self, cmd: CreateItemCmd) -> Item:
        new_item = Item(title=cmd.title, description=cmd.description)

        async with self.uow():
            await self.repo.create(new_item)

        return new_item


class UpdateItemUseCase(UseCase):
    def __init__(self, repo: ItemRepository, uow: UowFactory):
        self.repo = repo
        self.uow = uow

    async def execute(self, cmd: UpdateItemCmd) -> Item:
        async with self.uow():
            item = await self.repo.get_by_id(cmd.item_id)

            item.rename(cmd.title)  # FIXME in cmd at now can be None, but domain entity isn't allow the None value >:(
            item.set_description(cmd.description)

            await self.repo.update(item)

        return item


class DeleteItemUseCase(UseCase):
    def __init__(self, repo: ItemRepository, uow: UowFactory):
        self.repo = repo
        self.uow = uow

    async def execute(self, cmd: DeleteItemCmd) -> None:
        async with self.uow():
            await self.repo.delete(cmd.item_id)
