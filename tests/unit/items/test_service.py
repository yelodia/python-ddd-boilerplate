import pytest

from src.core.items.exceptions import ItemNotFoundError
from src.core.items.service import ItemService
from src.infrastructure.in_memory.repositories.items import InMemoryItemRepository


@pytest.fixture
def service() -> ItemService:
    return ItemService(InMemoryItemRepository())


async def test_create_and_get(service: ItemService) -> None:
    item = await service.create_item(title="Test", description="desc")
    found = await service.get_item(item.id)
    assert found.title == "Test"
    assert found.description == "desc"


async def test_get_not_found(service: ItemService) -> None:
    with pytest.raises(ItemNotFoundError):
        await service.get_item(999)


async def test_list_items(service: ItemService) -> None:
    await service.create_item(title="A")
    await service.create_item(title="B")
    items = await service.list_items(offset=0, limit=20)
    assert len(items) == 2


async def test_list_items_with_offset(service: ItemService) -> None:
    for i in range(5):
        await service.create_item(title=f"Item {i}")
    items = await service.list_items(offset=2, limit=2)
    assert len(items) == 2
    assert items[0].title == "Item 2"


async def test_update_title(service: ItemService) -> None:
    item = await service.create_item(title="Old")
    updated = await service.update_item(item.id, title="New")
    assert updated.title == "New"
    assert updated.id == item.id


async def test_update_description(service: ItemService) -> None:
    item = await service.create_item(title="T", description="old desc")
    updated = await service.update_item(item.id, description="new desc")
    assert updated.description == "new desc"
    assert updated.title == "T"


async def test_update_clear_description(service: ItemService) -> None:
    item = await service.create_item(title="T", description="has desc")
    updated = await service.update_item(item.id, description=None)
    assert updated.description is None


async def test_update_not_found(service: ItemService) -> None:
    with pytest.raises(ItemNotFoundError):
        await service.update_item(999, title="X")


async def test_delete(service: ItemService) -> None:
    item = await service.create_item(title="To delete")
    await service.delete_item(item.id)
    with pytest.raises(ItemNotFoundError):
        await service.get_item(item.id)


async def test_delete_not_found(service: ItemService) -> None:
    with pytest.raises(ItemNotFoundError):
        await service.delete_item(999)
