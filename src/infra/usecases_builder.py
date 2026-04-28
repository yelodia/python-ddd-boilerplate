from typing import TypeVar, ClassVar, get_type_hints, AsyncContextManager

from arq.connections import ArqRedis

from application.event_bus_interface import EventBus
from application.event_handler_base import EventHandler
from application.posts.external_tool_interface import ExternalToolApiClient
from application.reports.report_storage import ReportStorage
from application.uow_interface import UnitOfWork, UowFactory
from application.use_case_base import UseCase
from config import settings, SQL, JSON, RAM
from core.exceptions import UnknownStorageError, UsecaseUnknownParamError
from core.items.repo_interfaces import ItemRepository
from core.shop.repo_interfaces import ProductRepository, CartRepository
from infra.event_bus.async_in_arq_worker import AsyncArqEventBus
from infra.event_bus.async_in_main_process import AsyncInProcessEventBus
from infra.event_handlers_registry import EVENT_HANDLERS
from infra.external_tool.dummy_api_client import DummyApiClient
from infra.reports.csv_report_storage import CsvReportStorage
from infra.storage.database.basic_stuff import get_session_factory
from infra.storage.database.repositories.item import SqlItemRepository
from infra.storage.database.uow import sql_unit_of_work
from infra.storage.json.repositories.item import JsonItemRepository
from infra.storage.json.repositories.shop import JsonProductRepository, JsonCartRepository
from infra.storage.json.uow import json_unit_of_work
from infra.storage.ram.repositories.item import RamItemRepository
from infra.storage.ram.repositories.shop import RamProductRepository, InMemoryCartRepository
from infra.storage.ram.uow import in_memory_unit_of_work
from infra.ws.publishers.ws_in_main_process import InProcessWsPublisher
from infra.ws_events_registry import WS_EVENTS
from infra.ws_manager import ws_manager

S = TypeVar('S')
RepoRegistry = dict[type, type]


class UseCasesBuilder:
    """
    Этот класс - фабрика подготовки юзкейсов и хэндлеров. Он изначально не знает, какие репозитории, UoW и прочие штуки
    нужны для каждого юзкейса или обработчика события, однако он может читать сигнатуры их конструкторов и
    самостоятельно подготавливать к работе объекты нужных классов.

    Также он является местом регистрации разных реализаций репозиториев, потому что какую из реализаций использовать -
    указывается в глобальных настройках (или вовсе в .env), а юзкейсы и хэндлеры вообще ничего не должны знать про это.

    При появлении в системе нового репозитория (в любом домене) - необходимо его "зарегистрировать", т.е.
    связать абстрактный интерфейс репозитория с его конкретной реализацией для каждого из поддерживаемых типов
    хранилищ (SQL, JSON, RAM) в нижеследующих словарях.

    Словарь - вид хранилища; ключ - интерфейс репозитория; значение - класс его реализации под этот вид хранилища.

    Сами юзкейсы и хэндлеры сюда тащить не нужно! Этим занимаются конечные точки (эндпоинты), вьюхи или кто-то ещё:
        - сами себе импортируют откуда-то класс юзкейса / хэндлера (БЕЗ ЕГО ИНИЦИАЛИЗАЦИИ!)
        - сами скармливают его билдеру в `get_use_case()` или '.build_handler()' (напрямую или через Depends - не суть)
        - билдер выполняет свою работу и возвращает уже готовый, полностью укомплектованный экземпляр юзкейса / хэндлера
        - ...
        - PROFIT!
    """

    def __init__(self, arq_client: ArqRedis | None = None):
        # Если передан arq_client — get_event_bus() вернёт AsyncArqEventBus (fire-and-forget через Redis).
        # Без него — AsyncInProcessEventBus (синхронная обработка событий в рамках текущего запроса).
        self._arq_client = arq_client

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
        ItemRepository: RamItemRepository,
        ProductRepository: RamProductRepository,
        CartRepository: InMemoryCartRepository,
    }

    @classmethod
    def _all_repo_interfaces(cls) -> tuple[type, ...]:
        all_interfaces = cls.SQL.keys() | cls.JSON.keys() | cls.RAM.keys()
        return tuple(all_interfaces)

    def _inject_params(self, cls: type, *, event_bus: EventBus | None = None) -> dict:
        hints = get_type_hints(cls.__init__)  # dict[str, type]
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
                # Юзкейс получает свежую шину; хэндлер — ту же шину, через которую пришло событие,
                # чтобы его новые события публиковались через ту же шину.
                input_params[param_name] = event_bus if event_bus is not None else self.get_event_bus()
                continue

            if annotation is ReportStorage:
                input_params[param_name] = self.get_report_storage()
                continue

            if annotation is ExternalToolApiClient:
                input_params[param_name] = self.get_external_tool_client()
                continue

            raise UsecaseUnknownParamError(
                f"Unknown parameter '{param_name}' with type '{annotation}' in '{cls.__name__}'"
            )

        return input_params

    def get_use_case(self, use_case_class: type[UseCase]) -> UseCase:
        return use_case_class(**self._inject_params(use_case_class))
        # FIXME рекомендовано полечить неким cast'ом, но я хз куда это пихать
        #  from typing import cast
        #  return cast(UseCase, use_case_class(**input_params))

    def build_handler(self, handler_class: type[EventHandler], event_bus: EventBus) -> EventHandler:
        return handler_class(**self._inject_params(handler_class, event_bus=event_bus))
        # FIXME рекомендовано полечить неким cast'ом, но я хз куда это пихать
        #  from typing import cast
        #  return cast(EventHandler, handler_class(**input_params))

    # region STORAGE THINGS

    def get_entity_repo(self, contract: type[S]) -> S:
        # Don't use self.ANY_DICT_OF_STORAGES.get() method here!
        # We want it to raise human-readable KeyError, but not a stupid "TypeError: 'NoneType' is not callable"
        # if contract is not declared in storage backend! Or just impement some custom error handling he if you want.

        if settings.storage_backend == SQL:
            return self.SQL[contract](get_session_factory())

        if settings.storage_backend == JSON:
            return self.JSON[contract](settings.json_data_dir)

        if settings.storage_backend == RAM:
            return self.RAM[contract]()

        raise UnknownStorageError(f"Unsupported storage backend: {settings.storage_backend}")

    @staticmethod
    def get_uow() -> AsyncContextManager[UnitOfWork]:
        if settings.storage_backend == SQL:
            return sql_unit_of_work(get_session_factory())

        if settings.storage_backend == JSON:
            return json_unit_of_work(settings.json_data_dir)

        if settings.storage_backend == RAM:
            return in_memory_unit_of_work()

        raise UnknownStorageError(f"Unsupported storage backend: {settings.storage_backend}")

    # endregion
    # region DOMAIN EVENTS AND WS ROUTING

    def get_event_bus(self) -> EventBus:
        ws_publisher = InProcessWsPublisher(ws_manager)
        if self._arq_client is not None:
            return AsyncArqEventBus(
                handlers_registry=EVENT_HANDLERS,
                arq_client=self._arq_client,
                ws_events_registry=WS_EVENTS,
                ws_publisher=ws_publisher,
            )
        return AsyncInProcessEventBus(
            handlers_registry=EVENT_HANDLERS,
            handler_factory=self.build_handler,
            ws_events_registry=WS_EVENTS,
            ws_publisher=ws_publisher,
        )

    # endregion
    # region EXTERNAL TOOLS AND REPORTS STUFF

    @staticmethod
    def get_report_storage() -> ReportStorage:
        return CsvReportStorage(settings.reports_storage_dir)

    @staticmethod
    def get_external_tool_client() -> ExternalToolApiClient:
        return DummyApiClient(base_url=settings.dummy_api_base_url, app_id=settings.dummy_api_app_id)

    # endregion
