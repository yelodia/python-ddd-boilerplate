from datetime import datetime

from src.core.auth.entities import UserData
from src.core.auth.repository import AbstractUserRepository


class InMemoryUserRepository(AbstractUserRepository):
    def __init__(self) -> None:
        self._users: dict[int, UserData] = {}
        self._next_id = 1

    async def get_by_id(self, user_id: int) -> UserData | None:
        return self._users.get(user_id)

    async def get_by_email(self, email: str) -> UserData | None:
        return next((u for u in self._users.values() if u.email == email), None)

    async def create(self, email: str, hashed_password: str) -> UserData:
        user = UserData(
            id=self._next_id,
            email=email,
            is_active=True,
            created_at=datetime.now(),
        )
        self._users[user.id] = user
        self._next_id += 1
        return user
