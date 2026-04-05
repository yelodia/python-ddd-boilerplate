from abc import ABC, abstractmethod

from src.core.items.entities import Item


class ItemRepository(ABC):
    @abstractmethod
    async def get_by_id(self, item_id: int) -> Item | None: ...

    @abstractmethod
    async def get_all(self, offset: int, limit: int) -> list[Item]: ...

    @abstractmethod
    async def create(self, title: str, description: str | None) -> Item:
        """
        FIXME: сюда должен передаваться готовый Item, а не данные для его сборки!
        Сборка Item должна происходить вне репозитория, например в юзкейсе,
        который пинает этот метод репозитория.
        Репозиторий должен заниматься только добычей сущностей из хранилища (восстановление)
        и добавлением сущностей в хранилище (сохранение), но не их созданием - это разные роли!
        """

    @abstractmethod
    async def update(self, item: Item) -> Item: ...

    @abstractmethod
    async def delete(self, item_id: int) -> None: ...
