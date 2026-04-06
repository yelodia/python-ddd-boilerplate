from abc import ABC, abstractmethod
from uuid import UUID

from src.core.items.entities import Item


class ItemRepository(ABC):
    @abstractmethod
    async def get_by_id(self, item_id: UUID) -> Item | None: ...

    @abstractmethod
    async def get_all(self, offset: int, limit: int) -> list[Item]: ...

    @abstractmethod
    async def create(self, item: Item): ...

    @abstractmethod
    async def update(self, item: Item) -> None: ...

    @abstractmethod
    async def delete(self, item_id: UUID) -> None: ...
