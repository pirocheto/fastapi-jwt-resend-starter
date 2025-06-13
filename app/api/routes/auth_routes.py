from typing import Any

from fastapi import APIRouter, status

from app.api.dependencies import AuthServiceDep, CredentialsDep, UserServiceDep
from app.schemas.auth import TokenPair
from app.schemas.user import UserRegister, UserRegisterResponse

router = APIRouter()


@router.post("/auth/register", response_model=UserRegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserRegister, user_service: UserServiceDep) -> Any:
    return await user_service.register_user(user_in)


@router.post("/auth/login", response_model=TokenPair, status_code=status.HTTP_200_OK)
async def login_user(credentials: CredentialsDep, auth_service: AuthServiceDep) -> Any:
    return await auth_service.login(email=credentials.username, password=credentials.password)


@router.post("/auth/refresh", response_model=TokenPair, status_code=status.HTTP_200_OK)
async def refresh_token(token: str, auth_service: AuthServiceDep) -> Any:
    # return await auth_service.refresh_token(token=token)
    ...
