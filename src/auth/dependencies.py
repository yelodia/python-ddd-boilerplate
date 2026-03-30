from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.repository import (
    AbstractUserRepository,
    JsonUserRepository,
    SqlUserRepository,
)
from src.auth.service import AuthService
from src.auth.use_cases import AuthUseCases
from src.config import Settings, get_settings
from src.dependencies import get_db


def get_user_repository(
    settings: Settings = Depends(get_settings),
    session: AsyncSession = Depends(get_db),
) -> AbstractUserRepository:
    if settings.use_json_storage:
        return JsonUserRepository(data_dir=settings.json_data_dir)
    return SqlUserRepository(session)


def get_auth_service(
    repo: AbstractUserRepository = Depends(get_user_repository),
) -> AuthService:
    return AuthService(repo)


def get_auth_use_cases(
    service: AuthService = Depends(get_auth_service),
) -> AuthUseCases:
    return AuthUseCases(service)


AuthUseCasesDep = Annotated[AuthUseCases, Depends(get_auth_use_cases)]
