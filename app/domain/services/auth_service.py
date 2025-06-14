from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions.auth_exceptions import (
    InvalidCredentialsError,
    InvalidPasswordResetTokenError,
    InvalidRefreshTokenError,
)
from app.domain.exceptions.user_exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.domain.models import User
from app.infrastructure.dao import PasswordResetTokenDAO, RefreshTokenDAO, UserDAO, VerificationTokenDAO
from app.infrastructure.db.models import PasswordResetTokenModel, RefreshTokenModel, UserModel, VerificationTokenModel
from app.infrastructure.email import mailer
from app.infrastructure.security import hashing, tokens
from app.schemas.auth import TokenPair, UserRegister
from app.utils import mapper


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_dao = UserDAO(session)
        self.refresh_token_dao = RefreshTokenDAO(session)
        self.verif_token_dao = VerificationTokenDAO(session)
        self.reset_token_dao = PasswordResetTokenDAO(session)

    async def register_user(self, *, user_in: UserRegister) -> User:
        """Register a new user."""

        async with self.session.begin():
            existing_user = await self.user_dao.get_by_email(email=user_in.email)
            if existing_user:
                raise UserAlreadyExistsError()

        # Prepare the user data for saving, excluding the password field
        user_dict = user_in.model_dump(exclude_unset=True, exclude={"password"})
        user_dict["hashed_password"] = hashing.get_password_hash(user_in.password)

        # Create a verification token for the new user
        opaque_token = tokens.create_opaque_token()
        hashed_opaque_token = hashing.get_token_hash(opaque_token)

        domain_user = User.model_validate(user_dict)
        db_user = mapper.domain_to_orm(domain_user, UserModel)

        db_verif_token = VerificationTokenModel(
            hashed_token=hashed_opaque_token,
            user=db_user,
        )

        async with self.session.begin():
            await self.user_dao.add(user=db_user)
            await self.verif_token_dao.add(verif_token=db_verif_token)

        email_data = mailer.generate_verification_email(
            email_to=domain_user.email,
            token=opaque_token,
        )
        mailer.send_email(
            email_to=domain_user.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
            raw_content=email_data.raw_content,
        )
        return domain_user

    async def login_user(self, *, email: str, password: str) -> TokenPair:
        """Authenticate user and return access and refresh tokens."""

        # Create an opaque token for refresh
        opaque_token = tokens.create_opaque_token()
        hashed_opaque_token = hashing.get_token_hash(opaque_token)

        async with self.session.begin():
            db_user = await self.user_dao.get_by_email(email=email)

            if not db_user:
                raise InvalidCredentialsError()

            if not hashing.verify_password(password, db_user.hashed_password):
                raise InvalidCredentialsError()

            db_refresh_token = RefreshTokenModel(
                hashed_token=hashed_opaque_token,
                user_id=db_user.id,
            )

            access_token = tokens.create_access_token(db_user.id)

            await self.refresh_token_dao.delete_by_user_id(user_id=db_user.id)
            await self.refresh_token_dao.add(refresh_token=db_refresh_token)

        return TokenPair(access_token=access_token, refresh_token=opaque_token)

    async def refresh_access_token(self, *, refresh_token: str) -> TokenPair:
        """Refresh the access token using a valid refresh token."""

        hashed_refresh_token = hashing.get_token_hash(refresh_token)

        opaque_token = tokens.create_opaque_token()
        hashed_opaque_token = hashing.get_token_hash(opaque_token)

        async with self.session.begin():
            db_refresh_token = await self.refresh_token_dao.get_by_token(hashed_refresh_token)

            if not db_refresh_token:
                raise InvalidRefreshTokenError()

            if db_refresh_token.expires_at < datetime.now(UTC):
                raise InvalidRefreshTokenError()

            db_new_refresh_token = RefreshTokenModel(
                hashed_token=hashed_opaque_token,
                user_id=db_refresh_token.user_id,
            )

            access_token = tokens.create_access_token(db_new_refresh_token.user_id)

            await self.refresh_token_dao.delete_by_user_id(db_new_refresh_token.user_id)
            await self.refresh_token_dao.add(db_new_refresh_token)

        return TokenPair(access_token=access_token, refresh_token=opaque_token)

    async def forgot_password(self, *, email: str) -> None:
        """Request a password reset link for the user."""

        # Create a verification token for password reset
        opaque_token = tokens.create_opaque_token()
        hashed_opaque_token = hashing.get_token_hash(opaque_token)

        async with self.session.begin():
            db_user = await self.user_dao.get_by_email(email=email)

            if not db_user:
                raise UserNotFoundError()

            db_reset_token = PasswordResetTokenModel(
                hashed_token=hashed_opaque_token,
                user_id=db_user.id,
            )

            # Required to access the email field later
            user_email = db_user.email

            await self.reset_token_dao.delete_by_user_id(user_id=db_user.id)
            await self.reset_token_dao.add(reset_token=db_reset_token)

        email_data = mailer.generate_password_reset_email(
            email_to=user_email,
            token=opaque_token,
        )
        mailer.send_email(
            email_to=user_email,
            subject=email_data.subject,
            html_content=email_data.html_content,
            raw_content=email_data.raw_content,
        )

    async def reset_password(self, *, token: str, new_password: str) -> None:
        """Reset user password using a valid token."""

        hashed_token = hashing.get_token_hash(token)
        new_hashed_password = hashing.get_password_hash(new_password)

        async with self.session.begin():
            db_reset_token = await self.reset_token_dao.get_by_token(hashed_token=hashed_token)

            if not db_reset_token:
                raise InvalidPasswordResetTokenError()

            if db_reset_token.expires_at < datetime.now(UTC):
                raise InvalidPasswordResetTokenError()

            await self.reset_token_dao.delete_by_user_id(user_id=db_reset_token.user_id)
            await self.user_dao.update_password(user_id=db_reset_token.user_id, hashed_password=new_hashed_password)

    async def verify_email(self, *, token: str) -> None:
        """Verify user email using a verification token."""

        hashed_token = hashing.get_token_hash(token)

        async with self.session.begin():
            db_verif_token = await self.verif_token_dao.get_by_token(hashed_token=hashed_token)

            if not db_verif_token:
                raise InvalidCredentialsError()

            if db_verif_token.expires_at < datetime.now(UTC):
                raise InvalidCredentialsError()

            await self.verif_token_dao.delete_by_user_id(user_id=db_verif_token.user_id)
            await self.user_dao.verify_email(user_id=db_verif_token.user_id)

    async def resend_verification_email(self, *, email: str) -> None:
        """Resend verification link to the user's email."""

        # Create a new verification token
        opaque_token = tokens.create_opaque_token()
        hashed_opaque_token = hashing.get_token_hash(opaque_token)

        async with self.session.begin():
            db_user = await self.user_dao.get_by_email(email=email)

            if not db_user:
                raise UserNotFoundError()

            db_verif_token = VerificationTokenModel(
                hashed_token=hashed_opaque_token,
                user_id=db_user.id,
            )

            # Required to access the email field later
            user_email = db_user.email

            await self.verif_token_dao.delete_by_user_id(user_id=db_user.id)
            await self.verif_token_dao.add(verif_token=db_verif_token)

        email_data = mailer.generate_verification_email(
            email_to=user_email,
            token=opaque_token,
        )
        mailer.send_email(
            email_to=user_email,
            subject=email_data.subject,
            html_content=email_data.html_content,
            raw_content=email_data.raw_content,
        )
