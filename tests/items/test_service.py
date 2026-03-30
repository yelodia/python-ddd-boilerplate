from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from src.items.domain import ItemData
from src.items.exceptions import ItemNotFoundError
from src.items.repository.abstract import AbstractItemRepository
from src.items.service import ItemService


def _make_item(item_id: int = 1, title: str = "Test") -> ItemData:
    return ItemData(
        id=item_id,
        title=title,
        description=None,
        is_active=True,
        created_at=datetime(2026, 1, 1),
    )


@pytest.fixture
def repo() -> AsyncMock:
    return AsyncMock(spec=AbstractItemRepository)


@pytest.fixture
def service(repo: AsyncMock) -> ItemService:
    return ItemService(repo)


async def test_get_item_found(service: ItemService, repo: AsyncMock) -> None:
    repo.get_by_id.return_value = _make_item()
    result = await service.get_item(1)
    assert result.id == 1
    repo.get_by_id.assert_awaited_once_with(1)


async def test_get_item_not_found(service: ItemService, repo: AsyncMock) -> None:
    repo.get_by_id.return_value = None
    with pytest.raises(ItemNotFoundError):
        await service.get_item(999)


async def test_list_items(service: ItemService, repo: AsyncMock) -> None:
    repo.get_all.return_value = [_make_item(1), _make_item(2, "Second")]
    result = await service.list_items(offset=0, limit=20)
    assert len(result) == 2
    repo.get_all.assert_awaited_once_with(offset=0, limit=20)


async def test_delete_item_not_found(service: ItemService, repo: AsyncMock) -> None:
    repo.get_by_id.return_value = None
    with pytest.raises(ItemNotFoundError):
        await service.delete_item(999)
