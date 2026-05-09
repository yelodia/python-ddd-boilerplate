"""Unit tests for InMemoryItemRepository."""

import pytest

from core.items.entities import Item
from core.items.exceptions import ItemAlreadyExistsError, ItemNotFoundError
from infra.storage.in_memory.repositories.item import InMemoryItemRepository


@pytest.fixture
def repo() -> InMemoryItemRepository:
    return InMemoryItemRepository()


def _make_item(**kwargs) -> Item:  # type: ignore[no-untyped-def]
    defaults = {"title": "Test", "description": None}
    defaults.update(kwargs)
    return Item(**defaults)


async def test_create_and_get(repo: InMemoryItemRepository) -> None:
    item = _make_item(title="Hello")
    await repo.create(item)
    found = await repo.get_by_id(item.id)
    assert found.title == "Hello"
    assert found.id == item.id


async def test_create_duplicate_raises(repo: InMemoryItemRepository) -> None:
    item = _make_item()
    await repo.create(item)
    with pytest.raises(ItemAlreadyExistsError):
        await repo.create(item)


async def test_get_not_found_raises(repo: InMemoryItemRepository) -> None:
    from uuid import uuid4

    with pytest.raises(ItemNotFoundError):
        await repo.get_by_id(uuid4())


async def test_get_slice(repo: InMemoryItemRepository) -> None:
    for i in range(5):
        await repo.create(_make_item(title=f"Item {i}"))
    items = await repo.get_slice(offset=0, limit=3)
    assert len(items) == 3


async def test_get_slice_with_offset(repo: InMemoryItemRepository) -> None:
    for i in range(5):
        await repo.create(_make_item(title=f"Item {i}"))
    items = await repo.get_slice(offset=3, limit=10)
    assert len(items) == 2


async def test_update(repo: InMemoryItemRepository) -> None:
    item = _make_item(title="Old")
    await repo.create(item)
    item.rename("New")
    await repo.update(item)
    found = await repo.get_by_id(item.id)
    assert found.title == "New"


async def test_delete(repo: InMemoryItemRepository) -> None:
    item = _make_item()
    await repo.create(item)
    await repo.delete(item.id)
    with pytest.raises(ItemNotFoundError):
        await repo.get_by_id(item.id)


async def test_delete_nonexistent_is_silent(repo: InMemoryItemRepository) -> None:
    from uuid import uuid4

    await repo.delete(uuid4())  # не должен бросать исключение
