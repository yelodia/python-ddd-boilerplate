from src.items.domain import ItemData
from src.items.exceptions import ItemNotFoundError
from src.items.repository.abstract import AbstractItemRepository
from src.items.schemas import ItemCreate


class ItemService:
    def __init__(self, repo: AbstractItemRepository) -> None:
        self.repo = repo

    async def get_item(self, item_id: int) -> ItemData:
        item = await self.repo.get_by_id(item_id)
        if not item:
            raise ItemNotFoundError(item_id)
        return item

    async def list_items(self, offset: int, limit: int) -> list[ItemData]:
        return await self.repo.get_all(offset=offset, limit=limit)

    async def create_item(self, data: ItemCreate) -> ItemData:
        return await self.repo.create(data)

    async def delete_item(self, item_id: int) -> None:
        item = await self.repo.get_by_id(item_id)
        if not item:
            raise ItemNotFoundError(item_id)
        await self.repo.delete(item_id)
