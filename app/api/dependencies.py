from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions.auth_exceptions import InvalidAccessTokenError
from app.domain.exceptions.user_exceptions import UserNotFoundError
from app.domain.models import User
from app.domain.services.auth_service import AuthService
from app.domain.services.user_service import UserService
from app.infrastructure.db.session import get_db
from app.infrastructure.security import tokens


async def get_current_user(user_service: "UserServiceDep", access_token: "AccessTokenDep") -> User:
    user_id = tokens.decode_access_token(access_token)
    if not user_id:
        raise InvalidAccessTokenError()
    user = await user_service.get_user_by_id(user_id=user_id)
    if not user:
        raise UserNotFoundError()
    return user


async def get_user_service(session: "AsyncSessionDep") -> UserService:
    return UserService(session=session)


async def get_auth_service(session: "AsyncSessionDep") -> AuthService:
    return AuthService(session=session)


# --- Service Dependencies ---
AsyncSessionDep = Annotated[AsyncSession, Depends(get_db)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]

# --- Authentication Dependencies ---
CredentialsDep = Annotated[OAuth2PasswordRequestForm, Depends()]
reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")
AccessTokenDep = Annotated[str, Depends(reusable_oauth2)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
