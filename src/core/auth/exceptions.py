class UserNotFoundError(Exception):
    def __init__(self, user_id: int) -> None:
        self.user_id = user_id
        super().__init__(f"User {user_id} not found")


class UserAlreadyExistsError(Exception):  # TODO: raise in create/register
    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(f"User with email '{email}' already exists")


class InvalidCredentialsError(Exception):  # TODO: raise in login
    def __init__(self) -> None:
        super().__init__("Invalid credentials")
