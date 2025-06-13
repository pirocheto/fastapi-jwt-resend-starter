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

# --- Database Dependency ---
AsyncSessionDep = Annotated[AsyncSession, Depends(get_db)]


# --- Services Dependencies ---
async def get_user_service(session: AsyncSessionDep) -> UserService:
    return UserService(session=session)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


async def get_auth_service(session: AsyncSessionDep) -> AuthService:
    return AuthService(session=session)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]

# --- Auth Dependencies ---
reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")
CredentialsDep = Annotated[OAuth2PasswordRequestForm, Depends()]
AccessTokenDep = Annotated[str, Depends(reusable_oauth2)]


async def get_current_user(user_service: UserServiceDep, access_token: AccessTokenDep) -> User:
    token_payload = tokens.decode_access_token(access_token)
    if not token_payload:
        raise InvalidAccessTokenError()
    user = await user_service.get_user_by_id(token_payload.sub)
    if not user:
        raise UserNotFoundError()
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
