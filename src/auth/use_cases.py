import structlog

from src.auth.schemas import UserResponse
from src.auth.service import AuthService

logger = structlog.get_logger(__name__)


class AuthUseCases:
    def __init__(self, service: AuthService) -> None:
        self.service = service

    async def get_user(self, user_id: int) -> UserResponse:
        user = await self.service.get_user(user_id)
        logger.info("user_fetched", user_id=user.id)
        return UserResponse.from_domain(user)
