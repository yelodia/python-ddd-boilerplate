from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from src.core.items.entities import ItemData


class ItemCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)


class ItemUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None


class ItemResponse(BaseModel):
    id: int
    title: str
    description: str | None
    is_active: bool
    created_at: datetime

    @classmethod
    def from_domain(cls, item: ItemData) -> ItemResponse:
        return cls(
            id=item.id,
            title=item.title,
            description=item.description,
            is_active=item.is_active,
            created_at=item.created_at,
        )
