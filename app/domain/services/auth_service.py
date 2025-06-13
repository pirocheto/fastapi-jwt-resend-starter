from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions.auth_exceptions import InvalidCredentialsError, InvalidRefreshTokenError
from app.domain.exceptions.user_exceptions import UserAlreadyExistsError
from app.domain.models import RefreshToken, User
from app.infrastructure.dao import RefreshTokenDAO, UserDAO, VerificationTokenDAO
from app.infrastructure.db.models import RefreshTokenModel, UserModel, VerificationTokenModel
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

    async def register_user(self, user_in: UserRegister) -> User:
        """Register a new user."""

        async with self.session.begin():
            existing_user = await self.user_dao.get_by_email(user_in.email)

        if existing_user:
            raise UserAlreadyExistsError()

        # Prepare the user data for saving, excluding the password field
        user_dict = user_in.model_dump(exclude_unset=True, exclude={"password"})
        user_dict["hashed_password"] = hashing.get_password_hash(user_in.password)

        domain_user = User.model_validate(user_dict)
        db_user = mapper.domain_to_orm(domain_user, UserModel)

        # Create a verification token for the new user
        opaque_token = tokens.create_opaque_token()
        hashed_opaque_token = hashing.get_token_hash(opaque_token)

        db_verif_token = VerificationTokenModel(hashed_token=hashed_opaque_token, user=db_user)

        async with self.session.begin():
            await self.user_dao.add(db_user)
            await self.verif_token_dao.add(db_verif_token)

        # Send verification email
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

    async def login(self, email: str, password: str) -> TokenPair:
        """Authenticate user and return access and refresh tokens."""

        async with self.session.begin():
            db_user = await self.user_dao.get_by_email(email)
            if not db_user:
                raise InvalidCredentialsError()
            domain_user = mapper.orm_to_domain(db_user, User)

        # Check if password is correct
        if not domain_user.check_password(password):
            raise InvalidCredentialsError()

        # Create standard JWT access token and hashed opaque refresh token
        access_token = tokens.create_access_token(domain_user.id)
        opaque_token = tokens.create_opaque_token()

        # Hash the opaque token for storage
        hashed_opaque_token = hashing.get_token_hash(opaque_token)
        db_refresh_token = RefreshTokenModel(hashed_token=hashed_opaque_token, user_id=domain_user.id)

        # Delete any existing refresh tokens for the user and save the new one
        # This ensures that only one refresh token is valid at a time
        async with self.session.begin():
            await self.refresh_token_dao.delete_by_user_id(user_id=domain_user.id)
            await self.refresh_token_dao.save(refresh_token=db_refresh_token)

        return TokenPair(access_token=access_token, refresh_token=opaque_token)

    async def refresh_access_token(self, refresh_token: str) -> TokenPair:
        """Refresh the access token using a valid refresh token."""

        hashed_refresh_token = hashing.get_token_hash(refresh_token)

        async with self.session.begin():
            db_refresh_token = await self.refresh_token_dao.get_by_token(hashed_refresh_token)

            if not db_refresh_token:
                raise InvalidRefreshTokenError()

            domain_refresh_token = mapper.orm_to_domain(db_refresh_token, RefreshToken)

        if domain_refresh_token.is_expired():
            raise InvalidRefreshTokenError()

        access_token = tokens.create_access_token(domain_refresh_token.user_id)
        opaque_token = tokens.create_opaque_token()
        hashed_opaque_token = hashing.get_token_hash(opaque_token)

        db_new_refresh_token = RefreshTokenModel(
            hashed_token=hashed_opaque_token,
            user_id=domain_refresh_token.user_id,
        )

        async with self.session.begin():
            await self.refresh_token_dao.delete_by_user_id(domain_refresh_token.user_id)
            await self.refresh_token_dao.save(db_new_refresh_token)

        return TokenPair(access_token=access_token, refresh_token=opaque_token)
