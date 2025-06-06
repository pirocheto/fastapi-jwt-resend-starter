from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.core import security
from app.core.config import settings
from app.core.database import SessionDep
from app.core.exceptions import (
    EmailNotVerifiedException,
    InactiveUserException,
    InvalidCredentialsException,
    UserNotFoundException,
)
from app.models import User
from app.services import user_service

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login/access-token")


TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    user_id = security.verify_access_token(token=token)

    if not user_id:
        raise InvalidCredentialsException()
    user = user_service.get_user_by_id(session=session, user_id=user_id)

    if not user:
        raise UserNotFoundException()
    if not user.is_active:
        raise InactiveUserException()
    if not user.email_verified:
        raise EmailNotVerifiedException()
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
