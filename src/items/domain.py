from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ItemData:
    id: int
    title: str
    description: str | None
    is_active: bool
    created_at: datetime


def is_valid_title(title: str) -> bool:
    return bool(title) and 1 <= len(title.strip()) <= 255


def make_title(raw: str) -> str:
    return raw.strip()
