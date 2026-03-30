from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class UserData:
    id: int
    email: str
    is_active: bool
    created_at: datetime
