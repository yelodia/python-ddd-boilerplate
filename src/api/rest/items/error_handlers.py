from starlette.status import HTTP_418_IM_A_TEAPOT

from core.items.exceptions import IAmTeapotError

"""NOTE: Please, each error should uses only in one of mechanics, but not both at time!"""

specific_status_codes = {
    IAmTeapotError: HTTP_418_IM_A_TEAPOT,
}
"""The map for any errors which should be responded with specific HTTP status code."""


custom_error_handlers = {}
"""
The declaration a custom handlers for exceptions of current domain.

Format: {
            ExceptionType: handler_function,
            AnotherExceptionType: another_handler_function,
            ...
        }

For example:
    we want a response not only with specific status code, bun also with some 
    custom content, which is not just "detail" field with error message.
    For implements it we should create custom handler function, which will be used
    only for this exception, and register it via ERROR_HANDLERS list.

Code example:
        from starlette.responses import JSONResponse

        specific_status_codes = {}


        def custom_handler(request, exc) -> JSONResponse:
            return JSONResponse(
                status_code=HTTP_418_IM_A_TEAPOT,
                content=dict(
                    detail=str(exc),
                    timestamp=datetime.now(),
                )
            )

        custom_error_handlers = {
            IAmTeapotError: custom_handler,
            IAnNotATeapotError: custom_handler,
        }

    Then only for two these exceptions will be used custom_handler(), and for all another exceptions,
    which are not listed in `custom_error_handlers`, but are subclass of DomainError - still be processed
    by default `domain_errors_handler()` handler from `api.rest.error_handlers` module.
"""
