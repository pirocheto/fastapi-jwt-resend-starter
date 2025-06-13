from typing import Any

from fastapi import APIRouter, status

from app.api.dependencies import AuthServiceDep, CredentialsDep
from app.schemas.auth import RefreshAccessTokenRequest, TokenPair, UserRegister, UserRegisterResponse

router = APIRouter()


@router.post("/auth/register", response_model=UserRegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserRegister, auth_service: AuthServiceDep) -> Any:
    """Register a new user and send verification email."""
    return await auth_service.register_user(user_in)


@router.post("/auth/login", response_model=TokenPair, status_code=status.HTTP_200_OK)
async def login_user(credentials: CredentialsDep, auth_service: AuthServiceDep) -> Any:
    """Authenticate user and return access and refresh tokens."""
    return await auth_service.login(email=credentials.username, password=credentials.password)


@router.post("/auth/refresh", response_model=TokenPair, status_code=status.HTTP_200_OK)
async def refresh_access_token(data: RefreshAccessTokenRequest, auth_service: AuthServiceDep) -> Any:
    """Refresh the access token using a valid refresh token."""
    return await auth_service.refresh_access_token(refresh_token=data.refresh_token)


# @router.post("/auth/forgot-password", status_code=status.HTTP_204_NO_CONTENT)
# async def forgot_password(email: str, user_service: UserServiceDep) -> Any:
#     """Request a password reset link for the user."""


# @router.post("/auth/reset-password", status_code=status.HTTP_204_NO_CONTENT)
# async def reset_password(token: str, new_password: str, user_service: AuthServiceDep) -> Any:
#     """Reset user password using a valid token."""


# @router.post("/auth/verify-email", status_code=status.HTTP_204_NO_CONTENT)
# async def verify_email(token: str, user_service: UserServiceDep) -> Any:
#     """Verify user email using a verification token."""


# @router.post("/auth/resend-verification", status_code=status.HTTP_204_NO_CONTENT)
# async def resend_verification(email: str, user_service: UserServiceDep) -> Any:
#     """Resend verification email to the user."""
