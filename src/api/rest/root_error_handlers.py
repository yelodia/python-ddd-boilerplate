from fastapi import FastAPI
from fastapi import status
from starlette.responses import JSONResponse

from api.rest.auth.error_handlers import (
    custom_error_handlers as auth_handlers,
    specific_status_codes as auth_specific_codes,
)
from api.rest.items.error_handlers import (
    custom_error_handlers as item_handlers,
    specific_status_codes as item_specific_codes,
)
from common.exceptions import DomainError, NotFoundError, RateLimitError

_DEFAULT_STATUS_CODE = status.HTTP_400_BAD_REQUEST
_STATUS_CODES: dict[type[Exception], int] = {
    DomainError: _DEFAULT_STATUS_CODE,
    NotFoundError: status.HTTP_404_NOT_FOUND,
    RateLimitError: status.HTTP_429_TOO_MANY_REQUESTS,  # TODO just for example
}
_STATUS_CODES.update(auth_specific_codes)
_STATUS_CODES.update(item_specific_codes)


async def default_domain_errors_handler(request, exc) -> JSONResponse:
    """
    Default exception handler for all DomainError exceptions, which can be raised in any domain.

    Any domain-specific exception handler should be registered before this one,
    because it will be used as fallback for all exceptions, which are not handled by more specific handlers.
    """
    status_code = next(
        (code for exc_type, code in _STATUS_CODES.items() if isinstance(exc, exc_type)),
        _DEFAULT_STATUS_CODE,
    )
    return JSONResponse(
        status_code=status_code,
        content={
            "detail": str(exc),
        }
    )


async def general_exception_handler(request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
        }
    )


def bind_handlers_to(app: FastAPI) -> None:
    """Bind all custom and default error handlers to the FastAPI app."""
    custom_handlers = {
        # add unpacking here for other custom handlers, if they exist
        **auth_handlers,
        **item_handlers,
    }

    for ext_type, handler in custom_handlers.items():
        app.add_exception_handler(ext_type, handler)

    for ext_type in _STATUS_CODES.keys():
        app.add_exception_handler(ext_type, default_domain_errors_handler)

    # also we can add some more general handlers for all another standard exceptions, for example:
    app.add_exception_handler(Exception, general_exception_handler)
