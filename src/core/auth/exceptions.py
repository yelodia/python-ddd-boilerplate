from common.exceptions import DomainError


class UserNotFoundError(DomainError):
    pass


class UserAlreadyExistsError(DomainError):
    pass


class InvalidCredentialsError(DomainError):
    pass
