from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from src.core.auth.entities import UserData


class UserResponse(BaseModel):
    id: int
    email: str
    is_active: bool
    created_at: datetime

    @classmethod
    def from_domain(cls, user: UserData) -> UserResponse:
        return cls(
            id=user.id,
            email=user.email,
            is_active=user.is_active,
            created_at=user.created_at,
        )
