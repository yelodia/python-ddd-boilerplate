from starlette import status

from src.core.auth.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
)


specific_status_codes = {
    # DomainErrorType: HTTP_STATUS_CODE,
    UserNotFoundError: status.HTTP_404_NOT_FOUND,
    UserAlreadyExistsError: status.HTTP_409_CONFLICT,
    InvalidCredentialsError: status.HTTP_401_UNAUTHORIZED,
}

custom_error_handlers = {
    # DomainErrorType: handler_function,
}
