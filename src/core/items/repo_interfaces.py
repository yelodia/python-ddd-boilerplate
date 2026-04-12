from abc import ABC, abstractmethod
from uuid import UUID

from src.core.items.entities import Item


class ItemRepository(ABC):
    @abstractmethod
    async def get_by_id(self, item_id: UUID) -> Item: ...

    @abstractmethod
    async def get_slice(self, offset: int, limit: int) -> list[Item]: ...

    @abstractmethod
    async def create(self, item: Item) -> None: ...

    @abstractmethod
    async def update(self, item: Item) -> None: ...

    @abstractmethod
    async def delete(self, item_id: UUID) -> None: ...
