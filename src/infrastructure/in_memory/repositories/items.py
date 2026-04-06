from uuid import UUID

from core.items.exceptions import ItemAlreadyExistsError
# from infrastructure.bootstrap import register_repo, RAM, Registration
from src.core.items.entities import Item
from src.core.items.repository import ItemRepository


class InMemoryItemRepository(ItemRepository):
    def __init__(self) -> None:
        self._items: dict[UUID, Item] = {}

    async def get_by_id(self, id: UUID) -> Item | None:
        return self._items.get(id)

    async def get_all(self, offset: int = 0, limit: int = 20) -> list[Item]:
        items = sorted(self._items.values(), key=lambda i: i.id)
        return items[offset:offset+limit]

    async def create(self, item: Item) -> None:
        if item.id in self._items.keys():
            raise ItemAlreadyExistsError(f"Item with ID {item.id} already exists")
        self._items[item.id] = item

    async def update(self, item: Item) -> None:
        self._items[item.id] = item

    async def delete(self, item_id: UUID) -> None:
        self._items.pop(item_id, None)


# Registration.register_repo(RAM, ItemRepository, InMemoryItemRepository)
