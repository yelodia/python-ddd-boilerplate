import structlog

from src.items.domain import ItemData
from src.items.schemas import ItemCreate, ItemResponse
from src.items.service import ItemService

logger = structlog.get_logger(__name__)


class ItemUseCases:
    def __init__(self, service: ItemService) -> None:
        self.service = service

    async def get_item(self, item_id: int) -> ItemResponse:
        item: ItemData = await self.service.get_item(item_id)
        return ItemResponse.from_domain(item)

    async def list_items(self, offset: int, limit: int) -> list[ItemResponse]:
        items: list[ItemData] = await self.service.list_items(offset, limit)
        return [ItemResponse.from_domain(i) for i in items]

    async def create_item(self, data: ItemCreate) -> ItemResponse:
        item: ItemData = await self.service.create_item(data)
        logger.info("item_created", item_id=item.id, title=item.title)
        return ItemResponse.from_domain(item)

    async def delete_item(self, item_id: int) -> None:
        await self.service.delete_item(item_id)
        logger.info("item_deleted", item_id=item_id)
