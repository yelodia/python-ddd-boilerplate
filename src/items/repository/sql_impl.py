from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.items.domain import ItemData
from src.items.models import Item
from src.items.repository.abstract import AbstractItemRepository
from src.items.schemas import ItemCreate


class SqlItemRepository(AbstractItemRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, item_id: int) -> ItemData | None:
        result = await self.session.execute(select(Item).where(Item.id == item_id))
        item = result.scalar_one_or_none()
        return self._to_domain(item) if item else None

    async def get_all(self, offset: int = 0, limit: int = 20) -> list[ItemData]:
        result = await self.session.execute(select(Item).offset(offset).limit(limit))
        return [self._to_domain(i) for i in result.scalars().all()]

    async def create(self, data: ItemCreate) -> ItemData:
        item = Item(**data.model_dump())
        self.session.add(item)
        await self.session.flush()
        return self._to_domain(item)

    async def delete(self, item_id: int) -> None:
        result = await self.session.execute(select(Item).where(Item.id == item_id))
        item = result.scalar_one_or_none()
        if item:
            await self.session.delete(item)
            await self.session.flush()

    def _to_domain(self, item: Item) -> ItemData:
        return ItemData(
            id=item.id,
            title=item.title,
            description=item.description,
            is_active=item.is_active,
            created_at=item.created_at,
        )
