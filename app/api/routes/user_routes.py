from typing import Any

from fastapi import APIRouter

from app.api.dependencies import CurrentUserDep, UserServiceDep
from app.schemas.user import UserDetail

router = APIRouter()


@router.get("/users/me", response_model=UserDetail)
async def get_current_user(current_user: CurrentUserDep, user_service: UserServiceDep) -> Any:
    return await user_service.get_user_by_id(current_user.id)
