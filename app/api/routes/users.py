from fastapi import APIRouter

from app.api.dependencies.auth import CurrentUser
from app.schemas.base import APIResponse
from app.schemas.user import UserOut

router = APIRouter(tags=["users"])


@router.get("/users/me")
def read_user_me(current_user: CurrentUser) -> APIResponse[UserOut]:
    """
    Get current user.
    """
    user = UserOut.model_validate(current_user)

    return APIResponse[UserOut](
        status="success",
        code="user_retrieved",
        message="User retrieved successfully",
        data=user,
    )
