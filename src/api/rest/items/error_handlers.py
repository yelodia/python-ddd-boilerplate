from src.core.items.exceptions import ItemAlreadyExistsError, ItemNotFoundError

http_codes = {
    ItemNotFoundError: 404,
    ItemAlreadyExistsError: 409,
}  # TODO придумать, как организовать маппинг доменных ошибок к HTTP-кодам
# TODO как пробросить эту "карту" на уровень выше, в общедоменный api/rest/exception_handlers.py


def get_exception_handlers(request, exc):  # другой пример "мапинга" бизнесовых ошибок оп HTTP-кодам
    status_code = 400

    if isinstance(exc, UserNotFoundError):
        status_code = 404

    if isinstance(exc, RateLimitError):
        status_code = 429

    return JSONResponse(status_code=status_code, content={"detail": str(exc)})
