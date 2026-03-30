from src.exceptions import AppError


class ItemNotFoundError(AppError):
    def __init__(self, item_id: int) -> None:
        super().__init__(f"Item {item_id} not found", status_code=404)


class ItemAlreadyExistsError(AppError):
    def __init__(self, title: str) -> None:
        super().__init__(f"Item with title '{title}' already exists", status_code=409)
