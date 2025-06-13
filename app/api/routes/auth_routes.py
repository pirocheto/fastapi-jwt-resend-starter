from typing import Annotated, Any

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import AuthServiceDep, UserServiceDep
from app.schemas.auth_dto import TokenPairDTO
from app.schemas.user_dto import UserRegisterDTO, UserRegisterResponseDTO

router = APIRouter()


@router.post("/auth/register", response_model=UserRegisterResponseDTO, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserRegisterDTO, user_service: UserServiceDep) -> Any:
    return await user_service.register_user(user_in)


@router.post("/auth/login", response_model=TokenPairDTO, status_code=status.HTTP_200_OK)
async def login_user(
    credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthServiceDep,
) -> Any:
    return await auth_service.login(email=credentials.username, password=credentials.password)
