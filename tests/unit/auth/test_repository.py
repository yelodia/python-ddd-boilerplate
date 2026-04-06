"""Contract tests: one test suite, multiple repository implementations."""

import pytest

from src.core.auth.repository import UserRepository
from infrastructure.file_storage.repositories.users import JsonUserRepository
from src.infrastructure.in_memory.repositories.auth import InMemoryUserRepository


@pytest.fixture(params=["in_memory", "json"])
async def repo(request: pytest.FixtureRequest, tmp_path) -> UserRepository:
    if request.param == "in_memory":
        return InMemoryUserRepository()
    (tmp_path / "users.json").write_text("[]")
    return JsonUserRepository(data_dir=str(tmp_path))


async def test_create_returns_user(repo: UserRepository) -> None:
    user = await repo.create(email="test@example.com", hashed_password="hash")
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.is_active is True


async def test_get_by_id(repo: UserRepository) -> None:
    created = await repo.create(email="find@example.com", hashed_password="hash")
    found = await repo.get_by_id(created.id)
    assert found is not None
    assert found.email == "find@example.com"


async def test_get_by_id_not_found(repo: UserRepository) -> None:
    result = await repo.get_by_id(99999)
    assert result is None


async def test_get_by_email(repo: UserRepository) -> None:
    await repo.create(email="alice@example.com", hashed_password="hash")
    found = await repo.get_by_email("alice@example.com")
    assert found is not None
    assert found.email == "alice@example.com"


async def test_get_by_email_not_found(repo: UserRepository) -> None:
    result = await repo.get_by_email("nobody@example.com")
    assert result is None
