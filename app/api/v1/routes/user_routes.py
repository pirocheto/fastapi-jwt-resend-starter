from fastapi import APIRouter

from app.domain.services.user_service import UserService
from app.schemas.user_dto import UserRegisterDTO, UserRegisterResponseDTO

router = APIRouter()


@router.post("/auth/register")
def register(user_in: UserRegisterDTO) -> UserRegisterResponseDTO:
    user_service = UserService()

    user = user_service.register_user(user_in)
    return UserRegisterResponseDTO(
        status="success",
        code="user_registered",
        user_id=user.id,
        email=user.email,
    )
