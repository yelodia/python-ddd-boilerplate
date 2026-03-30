from src.auth.domain import UserData
from src.auth.exceptions import UserNotFoundError
from src.auth.repository.abstract import AbstractUserRepository


class AuthService:
    def __init__(self, repo: AbstractUserRepository) -> None:
        self.repo = repo

    async def get_user(self, user_id: int) -> UserData:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)
        return user

    async def get_user_by_email(self, email: str) -> UserData | None:
        return await self.repo.get_by_email(email)
