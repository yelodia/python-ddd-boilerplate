"""Contract tests: one test suite, multiple repository implementations."""
# FIXME требует актуализации - интерфейс репозитория был изменен!

import pytest

from core.items.repo_interfaces import ItemRepository
from infra.storage.json.repositories.item import JsonItemRepository
from infra.storage.ram.repositories.item import RamItemRepository


@pytest.fixture(params=["in_memory", "json"])
async def repo(request: pytest.FixtureRequest, tmp_path) -> ItemRepository:
    if request.param == "in_memory":
        return RamItemRepository()
    (tmp_path / "items.json").write_text("[]")
    return JsonItemRepository(data_dir=str(tmp_path))


async def test_create_returns_item(repo: ItemRepository) -> None:
    item = await repo.create(title="Test", description="desc")
    assert item.id is not None
    assert item.title == "Test"
    assert item.description == "desc"
    assert item.is_active is True


async def test_get_by_id(repo: ItemRepository) -> None:
    created = await repo.create(title="Find me", description=None)
    found = await repo.get_by_id(created.id)
    assert found is not None
    assert found.id == created.id
    assert found.title == "Find me"


async def test_get_by_id_not_found(repo: ItemRepository) -> None:
    result = await repo.get_by_id(99999)
    assert result is None


async def test_get_all(repo: ItemRepository) -> None:
    await repo.create(title="A", description=None)
    await repo.create(title="B", description=None)
    items = await repo.get_slice(offset=0, limit=20)
    assert len(items) == 2


async def test_get_all_with_offset(repo: ItemRepository) -> None:
    for i in range(5):
        await repo.create(title=f"Item {i}", description=None)
    items = await repo.get_slice(offset=2, limit=2)
    assert len(items) == 2


async def test_update(repo: ItemRepository) -> None:
    item = await repo.create(title="Old", description=None)
    updated_item = item.update_title("New")
    result = await repo.update(updated_item)
    assert result.title == "New"
    found = await repo.get_by_id(item.id)
    assert found is not None
    assert found.title == "New"


async def test_delete(repo: ItemRepository) -> None:
    item = await repo.create(title="Delete me", description=None)
    await repo.delete(item.id)
    assert await repo.get_by_id(item.id) is None


async def test_delete_nonexistent(repo: ItemRepository) -> None:
    await repo.delete(99999)
