import structlog

from src.core.items.entities import ItemData
from src.core.items.service import ItemService

logger = structlog.get_logger(__name__)


class ItemUseCases:
    def __init__(self, service: ItemService) -> None:
        self.service = service

    async def get_item(self, item_id: int) -> ItemData:
        return await self.service.get_item(item_id)

    async def list_items(self, offset: int, limit: int) -> list[ItemData]:
        return await self.service.list_items(offset, limit)

    async def create_item(self, title: str, description: str | None = None) -> ItemData:
        item = await self.service.create_item(title=title, description=description)
        logger.info("item_created", item_id=item.id, title=item.title)
        return item

    async def update_item(
        self, item_id: int, title: str | None = None, description: str | None = ...
    ) -> ItemData:
        item = await self.service.update_item(item_id, title=title, description=description)
        logger.info("item_updated", item_id=item.id)
        return item

    async def delete_item(self, item_id: int) -> None:
        await self.service.delete_item(item_id)
        logger.info("item_deleted", item_id=item_id)
