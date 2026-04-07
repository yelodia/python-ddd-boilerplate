from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.items.entities import Item as ItemEntity
from core.items.exceptions import ItemNotFoundError
from core.items.repository import ItemRepository
from infrastructure.database.orm_models.items import Item as ItemORM
# from infrastructure.bootstrap import register_repo, SQL, Registration


class SqlItemRepository(ItemRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, item_id: UUID) -> ItemEntity:
        result = await self.session.execute(select(ItemORM).where(ItemORM.id == item_id))
        item = result.scalar_one_or_none()
        if not item:
            raise ItemNotFoundError(f"Item with id {item_id} not found")
        return self._to_domain(item)

    async def get_all(self, offset: int = 0, limit: int = 20) -> list[ItemEntity]:
        result = await self.session.execute(select(ItemORM).offset(offset).limit(limit))
        return [self._to_domain(i) for i in result.scalars().all()]

    async def create(self, item: ItemEntity) -> None:
        item_orm = ItemORM(
            id=item.id,
            title=item.title,
            description=item.description,
            is_active=bool(item.is_active),
            created_at=item.created_at,
        )
        self.session.add(item_orm)
        await self.session.flush()

    async def update(self, item: ItemEntity) -> None:
        result = await self.session.execute(select(ItemORM).where(ItemORM.id == item.id))
        item_orm = result.scalar_one()
        item_orm.title = item.title
        item_orm.description = item.description
        item_orm.is_active = item.is_active
        await self.session.flush()

    async def delete(self, item_id: UUID) -> None:
        result = await self.session.execute(select(ItemORM).where(ItemORM.id == item_id))
        item = result.scalar_one_or_none()
        if item:
            await self.session.delete(item)
            await self.session.flush()

    @staticmethod
    def _to_domain(item: ItemORM) -> ItemEntity:
        return ItemEntity(
            id=item.id,
            title=item.title,
            description=item.description,
            is_active=item.is_active,
            created_at=item.created_at,
        )


# Registration.register_repo(SQL, ItemRepository, SqlItemRepository)
