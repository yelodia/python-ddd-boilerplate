from src.exceptions import AppError


class UserNotFoundError(AppError):
    def __init__(self, user_id: int) -> None:
        super().__init__(f"User {user_id} not found", status_code=404)


class UserAlreadyExistsError(AppError):
    def __init__(self, email: str) -> None:
        super().__init__(f"User with email '{email}' already exists", status_code=409)


class InvalidCredentialsError(AppError):
    def __init__(self) -> None:
        super().__init__("Invalid credentials", status_code=401)
