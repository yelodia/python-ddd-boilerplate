from typing import TypeVar

from application.items.use_cases import (
    ShowAllItemsUseCase,
    GetItemUseCase,
    CreateItemUseCase,
    UpdateItemUseCase,
    DeleteItemUseCase,
)
from application.uow import UnitOfWork
from config import settings
from infra.database.base import SessionFactory
from infra.database.repositories.items import SqlItemRepository
from infra.database.uow import sql_unit_of_work
from infra.in_memory.repositories.items import InMemoryItemRepository
from infra.in_memory.uow import in_memory_unit_of_work
from infra.json_storage.repositories.items import JsonItemRepository
from infra.json_storage.uow import json_unit_of_work


def _uow() -> UnitOfWork:
    if settings.storage_backend == 'sql':
        return sql_unit_of_work(SessionFactory)

    if settings.storage_backend == 'json':
        return json_unit_of_work(settings.json_data_dir)

    if settings.storage_backend == 'ram':
        return in_memory_unit_of_work()

    raise ValueError(f"Unsupported storage backend: {settings.storage_backend}")


S = TypeVar('S')

SQL = 'sql'
JSON = 'json'
RAM = 'ram'

_registry: dict[str, dict[type, type]] = {
    'sql': {},
    'json': {},
    'ram': {},
}


class Registration:
    # def __init__(self):
    #     from infra.database.repositories.items import SqlItemRepository
    #     from infra.json_storage.repositories.items import JsonItemRepository
    #     from infra.in_memory.repositories.items import InMemoryItemRepository

    @classmethod
    def register_repo(cls, backend: str, contract: type, implementation: type) -> None:
        from pprint import pp
        _registry[backend][contract] = implementation
        pp(_registry, indent=4)


def register_repo(backend: str, contract: type, implementation: type):
    from pprint import pp
    _registry[backend][contract] = implementation
    pp(_registry, indent=4)


def get_repo(contract: type[S]) -> S:
    from pprint import pp
    implementation_class = _registry[settings.storage_backend].get(contract)
    pp(_registry, indent=4)
    return implementation_class(_uow())


class UnknownStorageError(Exception):
    pass


# ------------------- Repositories initialization -------------------
def item_repo():
    if settings.storage_backend == 'sql':
        return SqlItemRepository(SessionFactory)
    if settings.storage_backend == 'json':
        return JsonItemRepository(settings.json_data_dir)
    if settings.storage_backend == 'ram':
        return InMemoryItemRepository()

    raise UnknownStorageError(f"Unsupported storage backend: {settings.storage_backend}")


# ------------------- Use Cases initialization -------------------
def show_all_items_use_case() -> ShowAllItemsUseCase:
    # repo = get_repo(ItemRepository)
    return ShowAllItemsUseCase(item_repo())


def get_item_use_case() -> GetItemUseCase:
    return GetItemUseCase(item_repo())


def create_item_use_case() -> CreateItemUseCase:
    return CreateItemUseCase(item_repo(), _uow())


def update_item_use_case() -> UpdateItemUseCase:
    return UpdateItemUseCase(item_repo(), _uow())


def delete_item_use_case() -> DeleteItemUseCase:
    return DeleteItemUseCase(item_repo(), _uow())
