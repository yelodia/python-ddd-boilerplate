from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.auth.use_cases import AuthUseCases
from src.application.items.use_cases import ItemUseCases
from src.config import Settings, get_settings
from src.core.auth.repository import AbstractUserRepository
from src.core.auth.service import AuthService
from src.core.items.repository import AbstractItemRepository
from src.core.items.service import ItemService
from src.infrastructure.database.base import get_session
from src.infrastructure.database.uow import UnitOfWork
from src.infrastructure.ws_manager import ConnectionManager, manager


async def get_uow(
    session: AsyncSession | None = Depends(get_session),
) -> AsyncGenerator[UnitOfWork | None, None]:
    """Request-scoped UoW for mutating operations only (INSERT/UPDATE/DELETE).

    Inject as ``_uow: UowDep`` in views that modify data.
    FastAPI caches ``get_session`` per request, so the repo and UoW
    share the same underlying session — commit covers all repo writes.
    Read-only views should NOT depend on this.
    """
    if session is None:
        yield None
        return

    uow = UnitOfWork(session)
    try:
        yield uow
        await uow.commit()
    except Exception:
        await uow.rollback()
        raise


UowDep = Annotated[UnitOfWork | None, Depends(get_uow)]


def get_item_repository(
    settings: Settings = Depends(get_settings),
    session: AsyncSession | None = Depends(get_session),
) -> AbstractItemRepository:
    if settings.use_json_storage:
        from src.infrastructure.file_storage.repositories.items import JsonItemRepository

        return JsonItemRepository(data_dir=settings.json_data_dir)
    from src.infrastructure.database.repositories.items import SqlItemRepository

    assert session is not None
    return SqlItemRepository(session)


def get_item_service(
    repo: AbstractItemRepository = Depends(get_item_repository),
) -> ItemService:
    return ItemService(repo)


def get_item_use_cases(
    service: ItemService = Depends(get_item_service),
) -> ItemUseCases:
    return ItemUseCases(service)


def get_user_repository(
    settings: Settings = Depends(get_settings),
    session: AsyncSession | None = Depends(get_session),
) -> AbstractUserRepository:
    if settings.use_json_storage:
        from src.infrastructure.file_storage.repositories.auth import JsonUserRepository

        return JsonUserRepository(data_dir=settings.json_data_dir)
    from src.infrastructure.database.repositories.auth import SqlUserRepository

    assert session is not None
    return SqlUserRepository(session)


def get_auth_service(
    repo: AbstractUserRepository = Depends(get_user_repository),
) -> AuthService:
    return AuthService(repo)


def get_auth_use_cases(
    service: AuthService = Depends(get_auth_service),
) -> AuthUseCases:
    return AuthUseCases(service)


ItemUseCasesDep = Annotated[ItemUseCases, Depends(get_item_use_cases)]
AuthUseCasesDep = Annotated[AuthUseCases, Depends(get_auth_use_cases)]


def get_ws_manager() -> ConnectionManager:
    return manager


WsManagerDep = Annotated[ConnectionManager, Depends(get_ws_manager)]
