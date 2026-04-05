from dataclasses import dataclass, replace
from datetime import datetime


@dataclass(frozen=True)
class ItemData:
    id: int
    title: str
    description: str | None
    is_active: bool
    created_at: datetime

    def deactivate(self) -> "ItemData":  # TODO: wire to PATCH endpoint
        return replace(self, is_active=False)

    def activate(self) -> "ItemData":  # TODO: wire to PATCH endpoint
        return replace(self, is_active=True)

    def update_title(self, new_title: str) -> "ItemData":
        cleaned = new_title.strip()
        if not cleaned or len(cleaned) > 255:
            raise ValueError(f"Invalid item title: must be 1-255 chars, got {len(cleaned)}")
        return replace(self, title=cleaned)
