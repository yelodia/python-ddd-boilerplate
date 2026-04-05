from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.items.entities import Item as ItemEntity
from src.core.items.repository import ItemRepository
from src.infrastructure.database.models.items import Item as ORMItem


class SqlItemRepository(ItemRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, item_id: int) -> ItemEntity | None:
        result = await self.session.execute(select(ORMItem).where(ORMItem.id == item_id))
        item = result.scalar_one_or_none()
        return self._to_domain(item) if item else None

    async def get_all(self, offset: int = 0, limit: int = 20) -> list[ItemEntity]:
        result = await self.session.execute(select(ORMItem).offset(offset).limit(limit))
        return [self._to_domain(i) for i in result.scalars().all()]

    async def create(self, title: str, description: str | None) -> ItemEntity:
        item = Item(title=title, description=description)
        self.session.add(item)
        await self.session.flush()
        return self._to_domain(item)

    async def update(self, item: ItemEntity) -> ItemEntity:
        result = await self.session.execute(select(ORMItem).where(ORMItem.id == item.id))
        orm_item = result.scalar_one()
        orm_item.title = item.title
        orm_item.description = item.description
        orm_item.is_active = item.is_active
        await self.session.flush()
        return self._to_domain(orm_item)

    async def delete(self, item_id: int) -> None:
        result = await self.session.execute(select(ORMItem).where(ORMItem.id == item_id))
        item = result.scalar_one_or_none()
        if item:
            await self.session.delete(item)
            await self.session.flush()

    def _to_domain(self, item: ItemEntity) -> ItemEntity:
        return ItemEntity(
            id=item.id,
            title=item.title,
            description=item.description,
            is_active=item.is_active,
            created_at=item.created_at,
        )


def item_repository_factory(session) -> ItemRepository:
    return SqlItemRepository(session)
