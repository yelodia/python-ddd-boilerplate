"""Unit tests for Item entity — pure domain logic, no infrastructure."""

import pytest

from core.items.entities import Item
from core.items.exceptions import TitleCannotBeEmptyError, TitleTooLongError


def _make_item(title: str = "Test Item", description: str | None = None) -> Item:
    return Item(title=title, description=description)


class TestItemCreation:
    def test_creates_with_uuid(self) -> None:
        item = _make_item()
        assert item.id is not None

    def test_creates_inactive_by_default(self) -> None:
        item = _make_item()
        assert item.is_active is False

    def test_creates_with_timestamp(self) -> None:
        item = _make_item()
        assert item.created_at is not None


class TestItemRename:
    def test_rename(self) -> None:
        item = _make_item(title="Old")
        item.rename("New")
        assert item.title == "New"

    def test_rename_strips_whitespace(self) -> None:
        item = _make_item()
        item.rename("  trimmed  ")
        assert item.title == "trimmed"

    def test_rename_empty_raises(self) -> None:
        item = _make_item()
        with pytest.raises(TitleCannotBeEmptyError):
            item.rename("")

    def test_rename_whitespace_only_raises(self) -> None:
        item = _make_item()
        with pytest.raises(TitleCannotBeEmptyError):
            item.rename("   ")

    def test_rename_too_long_raises(self) -> None:
        item = _make_item()
        with pytest.raises(TitleTooLongError):
            item.rename("x" * 256)

    def test_rename_255_chars_ok(self) -> None:
        item = _make_item()
        item.rename("x" * 255)
        assert len(item.title) == 255


class TestItemDescription:
    def test_set_description(self) -> None:
        item = _make_item()
        item.set_description("new desc")
        assert item.description == "new desc"

    def test_clear_description(self) -> None:
        item = _make_item(description="has desc")
        item.set_description(None)
        assert item.description is None


class TestItemActivation:
    def test_activate(self) -> None:
        item = _make_item()
        item.activate()
        assert item.is_active is True

    def test_deactivate(self) -> None:
        item = _make_item()
        item.activate()
        item.deactivate()
        assert item.is_active is False
