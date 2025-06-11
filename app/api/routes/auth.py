from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies.auth import ActiveUser
from app.core.database import SessionDep
from app.core.exceptions import (
    EmailAlreadyVerified,
    EmailNotVerified,
    InvalidCredentials,
    PasswordIncorrect,
    PasswordResetTokenInvalid,
    PasswordResetTokenNotFound,
    RefreshTokenInvalid,
    RefreshTokenNotFound,
    UserInactive,
    UserNotFound,
    VerificationTokenInvalid,
    VerificationTokenNotFound,
)
from app.schemas.auth import (
    AccessTokenRefresh,
    PasswordReset,
    PasswordUpdate,
    PasswordUpdateToken,
    Tokens,
    VerificationResend,
)
from app.schemas.base import APIResponse
from app.schemas.user import UserCreate, UserRegister, UserUpdate
from app.services import email_service, token_service, user_service

router = APIRouter(tags=["auth"])


@router.post("/auth/token")
def login_for_access_token(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> APIResponse[Tokens]:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    try:
        user = user_service.authenticate(
            session=session,
            email=form_data.username,
            password=form_data.password,
        )
    except (UserNotFound, PasswordIncorrect):
        raise InvalidCredentials()

    access_token = token_service.create_access_token(db_user=user)
    refresh_token = token_service.create_refresh_token(session=session, db_user=user)

    return APIResponse[Tokens](
        status="success",
        code="user_login_success",
        message="User logged in successfully",
        data=Tokens(
            access_token=access_token,
            refresh_token=refresh_token.token,
        ),
    )


@router.post("/auth/token/refresh")
def refresh_access_token(session: SessionDep, data: AccessTokenRefresh) -> APIResponse[Tokens]:
    """
    Refresh the access token using a valid refresh token.
    """
    try:
        db_refresh_token = token_service.validate_refresh_token(session=session, token=data.refresh_token)
    except RefreshTokenNotFound:
        raise RefreshTokenInvalid()

    if not db_refresh_token.user.is_active:
        raise UserInactive()

    if not db_refresh_token.user.email_verified:
        raise EmailNotVerified()

    new_refresh_token = token_service.rotate_refresh_token(session=session, db_refresh_token=db_refresh_token)
    new_access_token = token_service.create_access_token(db_user=db_refresh_token.user)

    return APIResponse[Tokens](
        status="success",
        code="user_refresh_token_success",
        message="User access token refreshed successfully",
        data=Tokens(
            access_token=new_access_token,
            refresh_token=new_refresh_token.token,
        ),
    )


@router.post("/auth/register", status_code=status.HTTP_201_CREATED)
def register_new_user(session: SessionDep, data: UserRegister) -> APIResponse[None]:
    """
    Register a new user.
    """
    user_create = UserCreate.model_validate(data)
    db_user = user_service.create_user(session=session, user_create=user_create)

    token_data = token_service.create_email_verification_token(
        session=session,
        db_user=db_user,
    )

    email_data = email_service.generate_verification_email(
        email_to=db_user.email,
        username=db_user.username or db_user.email,
        token=token_data.token,
    )

    email_service.send_email(
        email_to=db_user.email,
        subject=email_data.subject,
        html_content=email_data.html_content,
        raw_content=email_data.raw_content,
    )

    return APIResponse(
        status="success",
        code="user_registered",
        message="User registered successfully. Please check your email to verify your account.",
    )


@router.post("/auth/password/forgot", status_code=status.HTTP_200_OK)
def forgot_password(session: SessionDep, data: PasswordReset) -> APIResponse[None]:
    """
    Send a password reset link to the user's email.
    """
    user = user_service.get_user_by_email(session=session, email=data.email)

    if not user.is_active:
        raise UserInactive()

    db_token = token_service.create_password_reset_token(
        session=session,
        db_user=user,
    )

    email_data = email_service.generate_password_reset_email(
        email_to=user.email,
        username=user.username or user.email,
        token=db_token.token,
    )

    email_service.send_email(
        email_to=user.email,
        subject=email_data.subject,
        html_content=email_data.html_content,
        raw_content=email_data.raw_content,
    )

    return APIResponse(
        status="success",
        code="password_reset_link_sent",
        message="Password reset link sent to your email. Please check your inbox.",
    )


@router.post("/auth/password/reset", status_code=status.HTTP_200_OK)
def update_password_with_token(session: SessionDep, data: PasswordUpdateToken) -> APIResponse[None]:
    """
    Update the user's password using a valid password reset token.
    """
    try:
        db_token = token_service.validate_password_reset_token(
            session=session,
            token=data.token,
        )
    except PasswordResetTokenNotFound:
        raise PasswordResetTokenInvalid()

    if not db_token.user.is_active:
        raise UserInactive()

    user_update = UserUpdate(password=data.new_password)

    user_service.update_user(
        session=session,
        db_user=db_token.user,
        user_in=user_update,
    )

    # Mark all password reset tokens for this user as used
    token_service.mark_password_reset_token_as_used(session=session, db_token=db_token)

    return APIResponse(
        status="success",
        code="password_updated",
        message="Password updated successfully. You can now log in with your new password.",
    )


@router.patch("/auth/password", status_code=status.HTTP_200_OK)
def update_password(session: SessionDep, current_user: ActiveUser, data: PasswordUpdate) -> APIResponse[None]:
    """
    Update the user's password.
    """
    user_service.validate_password(
        db_user=current_user,
        password=data.current_password,
    )

    user_update = UserUpdate(password=data.new_password)

    user_service.update_user(
        session=session,
        db_user=current_user,
        user_in=user_update,
    )

    return APIResponse(
        status="success",
        code="password_updated",
        message="Password updated successfully.",
    )


@router.get("/auth/verify-email", status_code=status.HTTP_200_OK)
def confirm_email_verification(
    session: SessionDep, token: str = Query(..., description="Email verification token")
) -> APIResponse[None]:
    """
    Confirm the user's email address using the token sent to their email.
    """

    try:
        db_token = token_service.validate_email_verification_token(
            session=session,
            token=token,
        )
    except VerificationTokenNotFound:
        raise VerificationTokenInvalid()

    if not db_token.user.is_active:
        raise UserInactive()
    if db_token.user.email_verified:
        raise EmailAlreadyVerified()

    user_update = UserUpdate(email_verified=True)

    user_service.update_user(
        session=session,
        db_user=db_token.user,
        user_in=user_update,
    )

    # Mark the email verification token as used
    token_service.mark_email_verification_token_as_used(session=session, db_token=db_token)

    return APIResponse(
        status="success",
        code="user_verified",
        message="User email verified successfully.",
    )


@router.post("/auth/resend-verification")
def resend_verification_email(session: SessionDep, data: VerificationResend) -> APIResponse[None]:
    """
    Resend the email verification link to the user.
    """
    db_user = user_service.get_user_by_email(session=session, email=data.email)

    if not db_user.is_active:
        raise UserInactive()
    if db_user.email_verified:
        raise EmailAlreadyVerified()

    db_token = token_service.create_email_verification_token(session=session, db_user=db_user)

    email_data = email_service.generate_verification_email(
        email_to=db_user.email,
        username=db_user.username or db_user.email,
        token=db_token.token,
    )

    email_service.send_email(
        email_to=db_user.email,
        subject=email_data.subject,
        html_content=email_data.html_content,
        raw_content=email_data.raw_content,
    )

    return APIResponse(
        status="success",
        code="verification_email_sent",
        message="Email verification link sent successfully. Please check your inbox.",
    )
