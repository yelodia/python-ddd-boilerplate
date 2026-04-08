import pytest

from core.auth.exceptions import UserNotFoundError
from core.auth.service import AuthService
from infra.in_memory.repositories.user import InMemoryUserRepository


@pytest.fixture
def service() -> AuthService:
    return AuthService(InMemoryUserRepository())


async def test_create_and_get(service: AuthService) -> None:
    repo = service.repo
    user = await repo.create(email="alice@example.com", hashed_password="hash123")
    found = await service.get_user(user.id)
    assert found.email == "alice@example.com"


async def test_get_not_found(service: AuthService) -> None:
    with pytest.raises(UserNotFoundError):
        await service.get_user(999)


async def test_get_by_email_found(service: AuthService) -> None:
    repo = service.repo
    await repo.create(email="bob@example.com", hashed_password="hash")
    found = await service.get_user_by_email("bob@example.com")
    assert found is not None
    assert found.email == "bob@example.com"


async def test_get_by_email_not_found(service: AuthService) -> None:
    result = await service.get_user_by_email("nobody@example.com")
    assert result is None
