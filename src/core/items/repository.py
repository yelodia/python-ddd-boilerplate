from abc import ABC, abstractmethod

from src.core.items.entities import ItemData


class AbstractItemRepository(ABC):
    @abstractmethod
    async def get_by_id(self, item_id: int) -> ItemData | None: ...

    @abstractmethod
    async def get_all(self, offset: int, limit: int) -> list[ItemData]: ...

    @abstractmethod
    async def create(self, title: str, description: str | None) -> ItemData: ...

    @abstractmethod
    async def update(self, item: ItemData) -> ItemData: ...

    @abstractmethod
    async def delete(self, item_id: int) -> None: ...
