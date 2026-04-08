from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.core.items.entities import Item


class ItemResponse(BaseModel):
    id: UUID
    title: str
    description: str | None
    is_active: bool
    created_at: datetime

    @classmethod
    def from_domain(cls, item: Item) -> ItemResponse:
        # TODO подумать над тем, как автоматически
        #  мапить доменные сущности в Response DTO
        return cls(
            id=item.id,
            title=item.title,
            description=item.description,
            is_active=bool(item.is_active),
            created_at=item.created_at,
        )
