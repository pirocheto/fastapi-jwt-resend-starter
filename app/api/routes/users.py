from typing import Any

from fastapi import APIRouter

from app.api.dependencies.auth import CurrentUser
from app.schemas.user import UserPublic

router = APIRouter(tags=["users"])


@router.get("/users/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> Any:
    """
    Get current user.
    """
    return current_user
