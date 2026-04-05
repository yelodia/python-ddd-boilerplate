class ItemNotFoundError(Exception):
    def __init__(self, item_id: int) -> None:
        self.item_id = item_id
        super().__init__(f"Item {item_id} not found")


class ItemAlreadyExistsError(Exception):  # TODO: raise in create when unique constraint needed
    def __init__(self, title: str) -> None:
        self.title = title
        super().__init__(f"Item with title '{title}' already exists")
