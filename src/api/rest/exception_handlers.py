from starlette.responses import JSONResponse

from common.exceptions import NotFoundError, RateLimitError

from api.rest.items.error_handlers import http_codes


async def domain_exception_handler(request, exc):
    status_code = 400

    if isinstance(exc, NotFoundError):
        status_code = 404

    if isinstance(exc, RateLimitError):
        status_code = 429

    return JSONResponse(status_code=status_code, content={"detail": str(exc)})
