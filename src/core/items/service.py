from src.core.items.entities import Item
from src.core.items.exceptions import ItemNotFoundError
from src.core.items.repository import AbstractItemRepository


class ItemService:
    def __init__(self, repo: AbstractItemRepository) -> None:
        self.repo = repo

    async def get_item(self, item_id: int) -> Item:
        item = await self.repo.get_by_id(item_id)
        if not item:
            raise ItemNotFoundError(f"Item {item_id} not found")
        return item

    async def list_items(self, offset: int, limit: int) -> list[Item]:
        return await self.repo.get_all(offset=offset, limit=limit)

    async def create_item(self, title: str, description: str | None = None) -> Item:
        return await self.repo.create(title=title, description=description)

    async def update_item(
        self, item_id: int, title: str | None = None, description: str | None = ...
    ) -> Item:
        item = await self.repo.get_by_id(item_id)
        if not item:
            raise ItemNotFoundError(f"Item {item_id} not found")
        if title is not None:
            item = item.update_title(title)
        if description is not ...:
            item = Item(
                id=item.id,
                title=item.title,
                description=description,
                is_active=item.is_active,
                created_at=item.created_at,
            )
        return await self.repo.update(item)

    async def delete_item(self, item_id: int) -> None:
        item = await self.repo.get_by_id(item_id)
        if not item:
            raise ItemNotFoundError(f"Item {item_id} not found")
        await self.repo.delete(item_id)
