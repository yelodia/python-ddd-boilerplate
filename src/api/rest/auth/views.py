from datetime import datetime, timezone

from fastapi import APIRouter
from starlette.requests import Request

# from src.api.dependencies import AuthUseCasesDep
from src.api.rest.auth.schemas import UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(request: Request) -> UserResponse:  # TODO just a stub for now, full rework required
    return UserResponse(
        id=1,
        email="user@example.com",
        is_active=True,
        created_at=datetime.now(tz=timezone.utc),
    )
# async def get_user(user_id: int, use_cases: AuthUseCasesDep) -> UserResponse:
#     user = await use_cases.get_user(user_id)
#     return UserResponse.from_domain(user)
