from typing import Annotated

from fastapi import APIRouter, Body, Depends, Query, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies.auth import CurrentUser
from app.core import messages, security
from app.core.config import settings
from app.core.database import SessionDep
from app.core.exceptions import (
    EmailAlreadyVerifiedException,
    EmailNotVerifiedException,
    InactiveUserException,
    InvalidCredentialsException,
    PasswordResetTokenInvalidException,
    UserAlreadyExistsException,
    UserNotFoundException,
    VerificationTokenInvalidException,
)
from app.schemas.auth import AccessToken, Tokens, UpdatePassword
from app.schemas.common import Message
from app.schemas.user import UserCreate, UserRegister, UserUpdate
from app.services import email_service, user_service

router = APIRouter(tags=["auth"])


@router.post("/auth/token")
def login_for_access_token(session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Tokens:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = user_service.authenticate(session=session, email=form_data.username, password=form_data.password)

    if not user:
        raise InvalidCredentialsException()

    if not user.is_active:
        raise InactiveUserException()

    if not user.email_verified:
        raise EmailNotVerifiedException()

    return Tokens(
        access_token=security.create_access_token(user.id),
        refresh_token=security.create_refresh_token(user.id),
        token_type="bearer",
    )


@router.post("/auth/token/refresh")
def refresh_access_token(session: SessionDep, refresh_token: Annotated[str, Body(..., embed=True)]) -> AccessToken:
    """
    Refresh the access token using a valid refresh token.
    """
    user_id = security.verify_refresh_token(token=refresh_token)
    if not user_id:
        raise InvalidCredentialsException()
    user = user_service.get_user_by_id(session=session, user_id=user_id)

    if not user:
        raise UserNotFoundException()
    if not user.is_active:
        raise InactiveUserException()
    if not user.email_verified:
        raise EmailNotVerifiedException()

    return AccessToken(access_token=security.create_access_token(user.id))


@router.post("/auth/register", status_code=status.HTTP_201_CREATED)
def register_new_user(session: SessionDep, user_in: UserRegister = Body(...)) -> Message:
    """
    Register a new user.
    """
    user = user_service.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise UserAlreadyExistsException()

    user_create = UserCreate.model_validate(user_in)
    new_user = user_service.create_user(session=session, user_create=user_create)

    token = security.create_email_verification_token(new_user.id)

    if settings.emails_enabled:
        email_data = email_service.generate_verification_email(
            email_to=new_user.email, username=new_user.username or new_user.email, token=token
        )

        email_service.send_email(
            email_to=new_user.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
            raw_content=email_data.raw_content,
        )

    return Message(message=messages.SUCCESS_USER_REGISTERED)


@router.post("/auth/password/forgot", status_code=status.HTTP_200_OK)
def send_email_reset_password(session: SessionDep, email: str = Body(..., embed=True)) -> Message:
    """
    Send a password reset link to the user's email.
    """
    user = user_service.get_user_by_email(session=session, email=email)
    if not user:
        raise UserNotFoundException()

    token = security.create_password_reset_token(subject=user.id)

    if settings.emails_enabled:
        email_data = email_service.generate_password_reset_email(
            email_to=user.email,
            username=user.username or user.email,
            token=token,
        )

        email_service.send_email(
            email_to=user.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
            raw_content=email_data.raw_content,
        )

    return Message(message=messages.SUCCESS_PASSWORD_RESET_LINK_SENT)


@router.post("/auth/password/reset", status_code=status.HTTP_200_OK)
def update_password_with_token(
    session: SessionDep,
    update_password: UpdatePassword,
) -> Message:
    """
    Update the user's password using a valid password reset token.
    """
    user_id = security.verify_password_reset_token(token=update_password.token)
    if not user_id:
        raise PasswordResetTokenInvalidException()

    user = user_service.get_user_by_id(session=session, user_id=user_id)

    if not user:
        raise UserNotFoundException()

    user_update = UserUpdate(password=update_password.new_password)
    user_service.update_user(session=session, db_user=user, user_in=user_update)

    return Message(message=messages.SUCCESS_PASSWORD_RESET)


@router.patch("/auth/password", status_code=status.HTTP_200_OK)
def update_password(session: SessionDep, current_user: CurrentUser, new_password: str = Body(..., embed=True)) -> Message:
    """
    Update the user's password.
    """
    user_update = UserUpdate(password=new_password)
    user_service.update_user(session=session, db_user=current_user, user_in=user_update)

    return Message(message=messages.SUCCESS_PASSWORD_UPDATED)


@router.get("/auth/verify-email", status_code=status.HTTP_200_OK)
def confirm_email_verification(session: SessionDep, token: str = Query(..., description="Email verification token")) -> Message:
    """
    Confirm the user's email address using the token sent to their email.
    """
    user_id = security.verify_email_verification_token(token=token)
    if not user_id:
        raise VerificationTokenInvalidException()

    user = user_service.get_user_by_id(session=session, user_id=user_id)

    if not user:
        raise UserNotFoundException()
    if user.email_verified:
        raise EmailAlreadyVerifiedException()

    user_service.verify_user_email(session=session, db_user=user)
    return Message(message=messages.SUCCESS_USER_VERIFIED)


@router.post("/auth/resend-verification", status_code=status.HTTP_200_OK)
def resend_verification_email(session: SessionDep, email: str = Body(..., embed=True)) -> Message:
    """
    Resend the email verification link to the user.
    """
    user = user_service.get_user_by_email(session=session, email=email)
    if not user:
        raise UserNotFoundException()

    if user.email_verified:
        raise EmailAlreadyVerifiedException()

    token = security.create_email_verification_token(subject=user.id)

    if settings.emails_enabled:
        email_data = email_service.generate_verification_email(
            email_to=user.email,
            username=user.username or user.email,
            token=token,
        )

        email_service.send_email(
            email_to=user.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
            raw_content=email_data.raw_content,
        )

    return Message(message=messages.SUCCESS_EMAIL_VERIFICATION_LINK_SENT)
