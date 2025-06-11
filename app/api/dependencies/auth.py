from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.core.database import SessionDep
from app.core.exceptions import EmailNotVerified, InvalidCredentials, UserInactive, UserNotFound
from app.models import User
from app.services import token_service

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")


TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        user = token_service.validate_access_token(session=session, token=token)
    except UserNotFound:
        raise InvalidCredentials()
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_active_user(session: SessionDep, user: CurrentUser) -> User:
    if not user.is_active:
        raise UserInactive()
    return user


ActiveUser = Annotated[User, Depends(get_active_user)]


def get_verified_user(session: SessionDep, user: ActiveUser) -> User:
    if not user.email_verified:
        raise EmailNotVerified()
    return user


VerifiedUser = Annotated[User, Depends(get_verified_user)]
