from abc import ABC, abstractmethod

from src.auth.domain import UserData
from src.auth.schemas import UserCreate


class AbstractUserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: int) -> UserData | None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> UserData | None: ...

    @abstractmethod
    async def create(self, data: UserCreate, hashed_password: str) -> UserData: ...
