from abc import ABC, abstractmethod

from src.core.auth.entities import UserData


class UserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: int) -> UserData | None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> UserData | None: ...

    @abstractmethod
    async def create(self, email: str, hashed_password: str) -> UserData: ...
