from abc import ABC, abstractmethod

from src.items.domain import ItemData
from src.items.schemas import ItemCreate


class AbstractItemRepository(ABC):
    @abstractmethod
    async def get_by_id(self, item_id: int) -> ItemData | None: ...

    @abstractmethod
    async def get_all(self, offset: int, limit: int) -> list[ItemData]: ...

    @abstractmethod
    async def create(self, data: ItemCreate) -> ItemData: ...

    @abstractmethod
    async def delete(self, item_id: int) -> None: ...
