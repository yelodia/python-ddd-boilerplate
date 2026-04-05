from dataclasses import dataclass, replace
from datetime import datetime


@dataclass(frozen=True)
class UserData:
    id: int
    email: str
    is_active: bool
    created_at: datetime

    def deactivate(self) -> "UserData":  # TODO: wire to admin endpoint
        return replace(self, is_active=False)

    def activate(self) -> "UserData":  # TODO: wire to admin endpoint
        return replace(self, is_active=True)
