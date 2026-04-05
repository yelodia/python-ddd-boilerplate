from fastapi import Request
from fastapi.responses import JSONResponse

from src.core.auth.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
)


async def user_not_found_handler(request: Request, exc: UserNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


async def user_already_exists_handler(request: Request, exc: UserAlreadyExistsError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


async def invalid_credentials_handler(request: Request, exc: InvalidCredentialsError) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": str(exc)})


exception_handlers = {
    UserNotFoundError: user_not_found_handler,
    UserAlreadyExistsError: user_already_exists_handler,
    InvalidCredentialsError: invalid_credentials_handler,
}
