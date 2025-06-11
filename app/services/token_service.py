from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session, joinedload

from app.core import security
from app.core.exceptions import (
    EmailNotVerified,
    InvalidAccessToken,
    PasswordResetTokenAlreadyUsed,
    PasswordResetTokenExpired,
    PasswordResetTokenNotFound,
    RefreshTokenExpired,
    RefreshTokenNotFound,
    RefreshTokenRevoked,
    UserInactive,
    UserNotFound,
    VerificationTokenAlreadyUsed,
    VerificationTokenExpired,
    VerificationTokenNotFound,
)
from app.models import EmailVerificationToken, PasswordResetToken, RefreshToken, User


def create_refresh_token(*, session: Session, db_user: User) -> RefreshToken:
    """
    Create a new refresh token for a user and save it to the database.
    """
    token_data = security.create_refresh_token()

    refresh_token = RefreshToken(
        user_id=db_user.id,
        token=token_data.token,
        issued_at=token_data.issued_at,
        expires_at=token_data.expires_at,
    )

    session.add(refresh_token)
    session.commit()
    session.refresh(refresh_token)
    return refresh_token


def create_access_token(*, db_user: User) -> str:
    token_data = security.create_access_token(user_id=db_user.id)
    return token_data.token


def validate_refresh_token(*, session: Session, token: str) -> RefreshToken:
    """
    Validate a refresh token by checking its existence, expiration, and revocation status.
    """
    statement = select(RefreshToken).options(joinedload(RefreshToken.user)).where(RefreshToken.token == token)
    db_token = session.execute(statement).scalar_one_or_none()

    if not db_token:
        raise RefreshTokenNotFound()
    if db_token.expires_at < datetime.now(UTC):
        raise RefreshTokenExpired()
    if db_token.is_revoked:
        raise RefreshTokenRevoked()
    return db_token


def validate_access_token(*, session: Session, token: str) -> User:
    """
    Validate an access token by verifying it and returning the associated user.
    """
    user_id = security.verify_access_token(token=token)

    if not user_id:
        raise InvalidAccessToken()

    statement = select(User).where(User.id == user_id)
    db_user = session.execute(statement).scalar_one_or_none()

    if not db_user:
        raise UserNotFound()
    if not db_user.is_active:
        raise UserInactive()
    if not db_user.email_verified:
        raise EmailNotVerified()
    return db_user


def validate_email_verification_token(*, session: Session, token: str) -> EmailVerificationToken:
    """
    Validate an email verification token by checking its existence and expiration.
    """
    statement = (
        select(EmailVerificationToken)
        .options(joinedload(EmailVerificationToken.user))
        .where(EmailVerificationToken.token == token)
    )
    db_token = session.execute(statement).scalar_one_or_none()

    if not db_token:
        raise VerificationTokenNotFound()
    if db_token.expires_at < datetime.now(UTC):
        raise VerificationTokenExpired()
    if db_token.used:
        raise VerificationTokenAlreadyUsed()
    return db_token


def validate_password_reset_token(*, session: Session, token: str) -> PasswordResetToken:
    """
    Validate a password reset token by checking its existence, expiration, and usage status.
    """
    statement = (
        select(PasswordResetToken)
        .options(joinedload(PasswordResetToken.user))
        .where(PasswordResetToken.token == token)
    )
    db_token = session.execute(statement).scalar_one_or_none()

    if not db_token:
        raise PasswordResetTokenNotFound()
    if db_token.expires_at < datetime.now(UTC):
        raise PasswordResetTokenExpired()
    if db_token.used:
        raise PasswordResetTokenAlreadyUsed()
    return db_token


def rotate_refresh_token(*, session: Session, db_refresh_token: RefreshToken) -> RefreshToken:
    """
    Rotate (replace) an existing refresh token with a new one.
    """
    statement = (
        update(RefreshToken)
        .where(
            RefreshToken.user_id == db_refresh_token.user_id,
            RefreshToken.expires_at < datetime.now(UTC),
            RefreshToken.is_revoked == False,  # noqa: E712 (False comparison)
        )
        .values(is_revoked=True)
    )
    session.execute(statement)

    token_data = security.create_refresh_token()

    new_refresh_db_token = RefreshToken(
        user_id=db_refresh_token.user_id,
        token=token_data.token,
        issued_at=token_data.issued_at,
        expires_at=token_data.expires_at,
    )

    session.add(new_refresh_db_token)
    session.flush()

    db_refresh_token.last_used_at = datetime.now(UTC)
    db_refresh_token.is_revoked = True
    db_refresh_token.replaced_by = new_refresh_db_token.id

    session.commit()
    session.refresh(new_refresh_db_token)

    return new_refresh_db_token


def create_email_verification_token(*, session: Session, db_user: User) -> EmailVerificationToken:
    """
    Create an email verification token for a user.
    """
    statement = (
        update(EmailVerificationToken)
        .where(
            EmailVerificationToken.user_id == db_user.id,
            EmailVerificationToken.expires_at < datetime.now(UTC),
            EmailVerificationToken.used == False,  # noqa: E712 (False comparison)
        )
        .values(used=True)
    )
    session.execute(statement)

    token_data = security.create_email_verification_token()

    email_verification_token = EmailVerificationToken(
        user_id=db_user.id,
        token=token_data.token,
        expires_at=token_data.expires_at,
    )

    session.add(email_verification_token)
    session.commit()
    session.refresh(email_verification_token)

    return email_verification_token


def create_password_reset_token(*, session: Session, db_user: User) -> PasswordResetToken:
    """
    Create a password reset token for a user.
    """
    statement = (
        update(PasswordResetToken)
        .where(
            PasswordResetToken.user_id == db_user.id,
            PasswordResetToken.expires_at < datetime.now(UTC),
            PasswordResetToken.used == False,  # noqa: E712 (False comparison)
        )
        .values(used=True)
    )
    session.execute(statement)

    token_data = security.create_password_reset_token()

    password_reset_token = PasswordResetToken(
        user_id=db_user.id,
        token=token_data.token,
        expires_at=token_data.expires_at,
    )

    session.add(password_reset_token)
    session.commit()
    session.refresh(password_reset_token)
    return password_reset_token
