from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.domain import UserData
from src.auth.models import User
from src.auth.repository.abstract import AbstractUserRepository
from src.auth.schemas import UserCreate


class SqlUserRepository(AbstractUserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: int) -> UserData | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        return self._to_domain(user) if user else None

    async def get_by_email(self, email: str) -> UserData | None:
        result = await self.session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        return self._to_domain(user) if user else None

    async def create(self, data: UserCreate, hashed_password: str) -> UserData:
        user = User(email=data.email, hashed_password=hashed_password)
        self.session.add(user)
        await self.session.flush()
        return self._to_domain(user)

    def _to_domain(self, user: User) -> UserData:
        return UserData(
            id=user.id,
            email=user.email,
            is_active=user.is_active,
            created_at=user.created_at,
        )
