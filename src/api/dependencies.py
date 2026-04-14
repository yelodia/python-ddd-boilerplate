from typing import Annotated

from fastapi import Depends, Request

from application.use_case_base import UseCase
from infra.usecases_builder import UseCasesBuilder
from infra.ws_manager import ConnectionManager, manager


def get_builder(request: Request) -> UseCasesBuilder:
    """
    Dependency-функция: собирает UseCasesBuilder для текущего запроса.

    arq_pool создаётся один раз при старте приложения (lifespan) и хранится в app.state.
    Передаём его в билдер — все юзкейсы и хэндлеры автоматически получат AsyncArqEventBus
    и смогут публиковать события в arq (fire-and-forget).
    """
    return UseCasesBuilder(arq_client=request.app.state.arq_pool)


def use_case_factory(use_case_class: type[UseCase]):
    async def dependency(
            builder: UseCasesBuilder = Depends(get_builder),
    ) -> UseCase:
        return builder.get_use_case(use_case_class)
    return dependency


def build(use_case_class: type[UseCase]):
    return Depends(use_case_factory(use_case_class))


def get_ws_manager() -> ConnectionManager:
    return manager


WsManagerDep = Annotated[ConnectionManager, Depends(get_ws_manager)]
