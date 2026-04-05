from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

from core.items.exceptions import CannotEmptyTitleError, TooLongTitleError


@dataclass(kw_only=True)
class Item:
    id: UUID = field(default_factory=uuid4)
    title: str
    description: str | None
    is_active: bool | None = False
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    def deactivate(self) -> None:  # TODO: wire to PATCH endpoint
        self.is_active = False

    def activate(self) -> None:  # TODO: wire to PATCH endpoint
        self.is_active = True

    def update_title(self, new_title: str) -> None:
        new_title = new_title.strip()

        if not new_title:
            raise CannotEmptyTitleError("Title cannot be empty")

        if len(new_title) > 255:
            raise TooLongTitleError(f"Title must be 1-255 chars, got {len(new_title)}")

        self.title = new_title
