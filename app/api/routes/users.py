from fastapi import APIRouter

from app.api.dependencies.auth import VerifiedUser
from app.schemas.base import DataAPIResponse
from app.schemas.user import UserOut

router = APIRouter(tags=["users"])


@router.get("/users/me")
async def read_user_me(current_user: VerifiedUser) -> DataAPIResponse[UserOut]:
    """
    Get current user.
    """
    user = UserOut.model_validate(current_user)

    return DataAPIResponse[UserOut](
        status="success",
        code="user_retrieved",
        message="User retrieved successfully",
        data=user,
    )
