from typing import TypeVar, ClassVar, get_type_hints, AsyncContextManager

from application.event_bus_interface import EventBus
from application.event_bus_stuff import handlers_map_factory
from application.uow_interface import UnitOfWork
from application.use_case_base import UseCase, UowFactory
from config import settings, SQL, JSON, RAM
from core.exceptions import UnknownStorageError, UsecaseUnknownParamError
from core.items.repo_interfaces import ItemRepository
from core.shop.repo_interfaces import ProductRepository, CartRepository
from infra.async_event_bus import async_event_bus_factory
from infra.storage.database.basic_stuff import SessionFactory
from infra.storage.database.repositories.item import SqlItemRepository
from infra.storage.database.uow import sql_unit_of_work
from infra.storage.in_memory.repositories.item import InMemoryItemRepository
from infra.storage.in_memory.repositories.shop import InMemoryProductRepository, InMemoryCartRepository
from infra.storage.in_memory.uow import in_memory_unit_of_work
from infra.storage.json_storage.repositories.item import JsonItemRepository
from infra.storage.json_storage.repositories.shop import JsonProductRepository, JsonCartRepository
from infra.storage.json_storage.uow import json_unit_of_work

S = TypeVar('S')
RepoRegistry = dict[type, type]


class UseCasesBuilder:
    """
    Этот класс - фабрика для юзкейсов. Он знает, какие репозитории, UoW и прочие штуки нужны для каждого юзкейса,
    однако он может читать сигнатуры их конструкторов и самостоятельно подготавливать к работе объекты нужных классов.

    При появлении в системе нового репозитория (в любом домене) - необходимо его "зарегистрировать".
    Т.е. связать абстрактный интерфейс репозитория с его конкретной реализацией для каждого из поддерживаемых типов
    хранилищ (SQL, JSON, RAM) в нижеследующих словарях.

    Словарь - вид хранилища, ключ - интерфейс репозитория, значение - класс его реализации под этот вид хранилища.

    Сами юзкейсы сюда тащить не нужно! Этим занимаются конечные точки (эндпоинты) и вьюхи:
        - импортируют откуда-то класс юзкейса (БЕЗ ЕГО ИНИЦИАЛИЗАЦИИ!)
        - скармливают его билдеру в метод `.get_use_case()` (напрямую или через Depends - не важно)
        - билдер выполняет свою работу и возвращает уже готовый, полностью укомплектованный экземпляр юзкейса
        - ...
        - PROFIT!
    """
    SQL: ClassVar[RepoRegistry] = {
        ItemRepository: SqlItemRepository,
        # TODO не хватает SQL-реализации для ProductRepository и CartRepository!
    }
    JSON: ClassVar[RepoRegistry] = {
        ItemRepository: JsonItemRepository,
        ProductRepository: JsonProductRepository,
        CartRepository: JsonCartRepository,
    }
    RAM: ClassVar[RepoRegistry] = {
        ItemRepository: InMemoryItemRepository,
        ProductRepository: InMemoryProductRepository,
        CartRepository: InMemoryCartRepository,
    }

    @classmethod
    def _all_repo_interfaces(cls) -> tuple[type, ...]:
        all_interfaces = cls.SQL.keys() | cls.JSON.keys() | cls.RAM.keys()
        return tuple(all_interfaces)

    def get_entity_repo(self, contract: type[S]) -> S:
        # Don't use self.ANY_DICT_OF_STORAGES.get() method here!
        # We want it to raise human-readable KeyError, but not a stupid "TypeError: 'NoneType' is not callable"
        # if contract is not declared in storage backend! Or just impement some custom error handling he if you want.

        if settings.storage_backend == SQL:
            return self.SQL[contract](SessionFactory)

        if settings.storage_backend == JSON:
            return self.JSON[contract](settings.json_data_dir)

        if settings.storage_backend == RAM:
            return self.RAM[contract]()

        raise UnknownStorageError(f"Unsupported storage backend: {settings.storage_backend}")

    def get_use_case(self, use_case_class: type[UseCase]) -> UseCase:
        hints = get_type_hints(use_case_class.__init__)  # dict[str, type]

        input_params = {}
        for param_name, annotation in hints.items():
            # get_type_hints() включает в словарь возвращаемый тип под ключом 'return'. Без этой проверки цикл
            # попытается создать зависимость для возвращаемого типа метода — и упадёт в UsecaseUnknownParamError.
            if param_name == 'return':
                continue

            if annotation is UowFactory:
                input_params[param_name] = self.get_uow
                continue

            if annotation in self._all_repo_interfaces():
                input_params[param_name] = self.get_entity_repo(annotation)
                continue

            if annotation is EventBus:
                input_params[param_name] = self.get_event_bus()
                continue

            raise UsecaseUnknownParamError(
                f"Unknown parameter '{param_name}' with type '{annotation}' in use case '{use_case_class.__name__}'")

        return use_case_class(**input_params)
        # FIXME рекомендовано полечить неким cast'ом, но я хз куда это пихать
        #  from typing import cast
        #  return cast(UseCase, use_case_class(**input_params))

    @staticmethod
    def get_uow() -> AsyncContextManager[UnitOfWork]:
        if settings.storage_backend == SQL:
            return sql_unit_of_work(SessionFactory)

        if settings.storage_backend == JSON:
            return json_unit_of_work(settings.json_data_dir)

        if settings.storage_backend == RAM:
            return in_memory_unit_of_work()

        raise UnknownStorageError(f"Unsupported storage backend: {settings.storage_backend}")

    @staticmethod
    def get_event_bus() -> EventBus:
        return async_event_bus_factory(handlers_map_factory())
