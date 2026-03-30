from fastapi import APIRouter

from src.auth.dependencies import AuthUseCasesDep
from src.auth.schemas import UserResponse

router = APIRouter()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, use_cases: AuthUseCasesDep) -> UserResponse:
    return await use_cases.get_user(user_id)
