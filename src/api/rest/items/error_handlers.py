from fastapi import Request
from fastapi.responses import JSONResponse

from src.core.items.exceptions import ItemAlreadyExistsError, ItemNotFoundError


async def item_not_found_handler(request: Request, exc: ItemNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


async def item_already_exists_handler(request: Request, exc: ItemAlreadyExistsError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


exception_handlers = {
    ItemNotFoundError: item_not_found_handler,
    ItemAlreadyExistsError: item_already_exists_handler,
}
