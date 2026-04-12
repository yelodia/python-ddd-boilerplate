from fastapi import FastAPI
from fastapi import status
from fastapi.exceptions import ValidationException
from starlette.responses import JSONResponse

from api.rest.items.error_handlers import (
    custom_error_handlers as item_handlers,
    specific_status_codes as item_specific_codes,
)
from common.exceptions import DomainError, NotFoundError, RateLimitError

_DEFAULT_STATUS_CODE = status.HTTP_400_BAD_REQUEST
_STATUS_CODES: dict[type[Exception], int] = {
    NotFoundError: status.HTTP_404_NOT_FOUND,
    RateLimitError: status.HTTP_429_TOO_MANY_REQUESTS,  # TODO just for example
}
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

async def views_validation_error_handler(request, exc) -> JSONResponse:
    """
    This handler is for validation errors, which can be raised in views, for example, when request body is invalid.

    We can also add some more specific handlers for validation errors in different views, if we want to return different status codes or error messages.
    """
    return JSONResponse(
        status_code=_DEFAULT_STATUS_CODE,
        content={
            "detail": str(exc),  # TODO сделать извлечение полнотекстового сообщения об ошибке
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
    """
    Bind all custom and default error handlers to the FastAPI app.

    The Rule:
        - First - specific handlers for specific exceptions
        - Then - default handler for all DomainError exceptions
        - Finally - generic handler for all other exceptions
    """
    custom_handlers = {
        # you should unpack here all other custom handlers, if they exist
        **item_handlers,
    }

    for ext_type, handler in custom_handlers.items():
        app.add_exception_handler(ext_type, handler)

    for ext_type in _STATUS_CODES.keys():
        app.add_exception_handler(ext_type, default_domain_errors_handler)

    app.add_exception_handler(DomainError, default_domain_errors_handler)

    # also we can add some more general handlers for all another standard exceptions, for example:
    app.add_exception_handler(ValidationException, views_validation_error_handler)
    app.add_exception_handler(Exception, general_exception_handler)
