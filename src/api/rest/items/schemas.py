from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.core.items.entities import Item


class ItemCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)


class ItemUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None


class ItemResponse(BaseModel):
    id: UUID
    title: str
    description: str | None
    is_active: bool
    created_at: datetime

    @classmethod
    def from_domain(cls, item: Item) -> ItemResponse:
        return cls(
            id=item.id,
            title=item.title,
            description=item.description,
            is_active=bool(item.is_active),
            created_at=item.created_at,
        )
