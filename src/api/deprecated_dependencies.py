# TODO remove this piece of... *code* after full re-implemented all dependencies mechanism
from typing import Annotated

from fastapi import Depends

from application.items.use_cases import ItemUseCases
from infra.ws_manager import ConnectionManager, manager





def get_ws_manager() -> ConnectionManager:
    return manager


WsManagerDep = Annotated[ConnectionManager, Depends(get_ws_manager)]
