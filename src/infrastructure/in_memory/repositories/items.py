from datetime import datetime

from src.core.items.entities import Item
from src.core.items.repository import AbstractItemRepository


class InMemoryItemRepository(AbstractItemRepository):
    def __init__(self) -> None:
        self._items: dict[int, Item] = {}
        self._next_id = 1

    async def get_by_id(self, item_id: int) -> Item | None:
        return self._items.get(item_id)

    async def get_all(self, offset: int = 0, limit: int = 20) -> list[Item]:
        items = sorted(self._items.values(), key=lambda i: i.id)
        return items[offset : offset + limit]

    async def create(self, title: str, description: str | None) -> Item:
        item = Item(
            id=self._next_id,
            title=title,
            description=description,
            is_active=True,
            created_at=datetime.now(),
        )
        self._items[item.id] = item
        self._next_id += 1
        return item

    async def update(self, item: Item) -> Item:
        self._items[item.id] = item
        return item

    async def delete(self, item_id: int) -> None:
        self._items.pop(item_id, None)
