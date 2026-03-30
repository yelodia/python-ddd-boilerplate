from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings, get_settings
from src.dependencies import get_db
from src.items.repository import (
    AbstractItemRepository,
    JsonItemRepository,
    SqlItemRepository,
)
from src.items.service import ItemService
from src.items.use_cases import ItemUseCases


def get_item_repository(
    settings: Settings = Depends(get_settings),
    session: AsyncSession = Depends(get_db),
) -> AbstractItemRepository:
    if settings.use_json_storage:
        return JsonItemRepository(data_dir=settings.json_data_dir)
    return SqlItemRepository(session)


def get_item_service(
    repo: AbstractItemRepository = Depends(get_item_repository),
) -> ItemService:
    return ItemService(repo)


def get_item_use_cases(
    service: ItemService = Depends(get_item_service),
) -> ItemUseCases:
    return ItemUseCases(service)


ItemUseCasesDep = Annotated[ItemUseCases, Depends(get_item_use_cases)]
