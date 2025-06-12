from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

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


async def create_refresh_token(*, async_session: AsyncSession, db_user: User) -> RefreshToken:
    token_data = security.create_refresh_token()

    refresh_token = RefreshToken(
        user_id=db_user.id,
        token=token_data.token,
        issued_at=token_data.issued_at,
        expires_at=token_data.expires_at,
    )

    statement = (
        update(RefreshToken)
        .where(
            RefreshToken.user_id == db_user.id,
            RefreshToken.is_revoked.is_(False),
        )
        .values(is_revoked=True)
    )
    await async_session.execute(statement)

    async_session.add(refresh_token)
    await async_session.commit()
    await async_session.refresh(refresh_token)
    return refresh_token


async def create_access_token(*, db_user: User) -> str:
    token_data = security.create_access_token(user_id=db_user.id)
    return token_data.token


async def validate_refresh_token(*, async_session: AsyncSession, token: str) -> RefreshToken:
    statement = select(RefreshToken).options(joinedload(RefreshToken.user)).where(RefreshToken.token == token)
    result = await async_session.execute(statement)
    db_token = result.scalar_one_or_none()

    if not db_token:
        raise RefreshTokenNotFound()
    if db_token.expires_at < datetime.now(UTC):
        raise RefreshTokenExpired()
    if db_token.is_revoked:
        raise RefreshTokenRevoked()
    return db_token


async def validate_access_token(*, async_session: AsyncSession, token: str) -> User:
    user_id = security.verify_access_token(token=token)

    if not user_id:
        raise InvalidAccessToken()

    statement = select(User).where(User.id == user_id)
    result = await async_session.execute(statement)
    db_user = result.scalar_one_or_none()

    if not db_user:
        raise UserNotFound()
    if not db_user.is_active:
        raise UserInactive()
    if not db_user.email_verified:
        raise EmailNotVerified()
    return db_user


async def validate_email_verification_token(*, async_session: AsyncSession, token: str) -> EmailVerificationToken:
    statement = (
        select(EmailVerificationToken)
        .options(joinedload(EmailVerificationToken.user))
        .where(EmailVerificationToken.token == token)
    )
    result = await async_session.execute(statement)
    db_token = result.scalar_one_or_none()

    if not db_token:
        raise VerificationTokenNotFound()
    if db_token.expires_at < datetime.now(UTC):
        raise VerificationTokenExpired()
    if db_token.used:
        raise VerificationTokenAlreadyUsed()
    return db_token


async def validate_password_reset_token(*, async_session: AsyncSession, token: str) -> PasswordResetToken:
    statement = (
        select(PasswordResetToken)
        .options(joinedload(PasswordResetToken.user))
        .where(PasswordResetToken.token == token)
    )
    result = await async_session.execute(statement)
    db_token = result.scalar_one_or_none()

    if not db_token:
        raise PasswordResetTokenNotFound()
    if db_token.expires_at < datetime.now(UTC):
        raise PasswordResetTokenExpired()
    if db_token.used:
        raise PasswordResetTokenAlreadyUsed()
    return db_token


async def rotate_refresh_token(*, async_session: AsyncSession, db_refresh_token: RefreshToken) -> RefreshToken:
    token_data = security.create_refresh_token()

    new_refresh_db_token = RefreshToken(
        user_id=db_refresh_token.user_id,
        token=token_data.token,
        issued_at=token_data.issued_at,
        expires_at=token_data.expires_at,
    )

    async_session.add(new_refresh_db_token)
    await async_session.flush()

    db_refresh_token.used_at = datetime.now(UTC)
    db_refresh_token.is_revoked = True
    db_refresh_token.replaced_by = new_refresh_db_token.id

    await async_session.commit()
    await async_session.refresh(new_refresh_db_token)

    return new_refresh_db_token


async def create_email_verification_token(*, async_session: AsyncSession, db_user: User) -> EmailVerificationToken:
    token_data = security.create_email_verification_token()

    email_verification_token = EmailVerificationToken(
        user_id=db_user.id,
        token=token_data.token,
        expires_at=token_data.expires_at,
    )

    statement = (
        update(EmailVerificationToken)
        .where(
            EmailVerificationToken.user_id == db_user.id,
            EmailVerificationToken.used.is_(False),
        )
        .values(used=True)
    )
    await async_session.execute(statement)

    async_session.add(email_verification_token)
    await async_session.commit()
    await async_session.refresh(email_verification_token)

    return email_verification_token


async def create_password_reset_token(*, async_session: AsyncSession, db_user: User) -> PasswordResetToken:
    token_data = security.create_password_reset_token()

    password_reset_token = PasswordResetToken(
        user_id=db_user.id,
        token=token_data.token,
        expires_at=token_data.expires_at,
    )

    statement = (
        update(PasswordResetToken)
        .where(
            PasswordResetToken.user_id == db_user.id,
            PasswordResetToken.used.is_(False),
        )
        .values(used=True)
    )
    await async_session.execute(statement)

    async_session.add(password_reset_token)
    await async_session.commit()
    await async_session.refresh(password_reset_token)
    return password_reset_token


async def mark_password_reset_token_as_used(
    *, async_session: AsyncSession, db_token: PasswordResetToken
) -> PasswordResetToken:
    db_token.used = True

    await async_session.commit()
    await async_session.refresh(db_token)
    return db_token


async def mark_email_verification_token_as_used(
    *, async_session: AsyncSession, db_token: EmailVerificationToken
) -> EmailVerificationToken:
    db_token.used = True

    await async_session.commit()
    await async_session.refresh(db_token)
    return db_token
