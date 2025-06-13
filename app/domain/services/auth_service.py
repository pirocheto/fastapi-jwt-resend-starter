from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions.auth_exceptions import InvalidCredentialsError
from app.domain.models import User
from app.infrastructure.dao import RefreshTokenDAO, UserDAO
from app.infrastructure.db.models import RefreshTokenModel
from app.infrastructure.db.utils import transactional
from app.infrastructure.security import hashing, tokens
from app.schemas.auth import TokenPair
from app.utils import mapper


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_dao = UserDAO(session)
        self.refresh_token_dao = RefreshTokenDAO(session)

    @transactional
    async def login(self, email: str, password: str) -> TokenPair:
        """Authenticate user and return access and refresh tokens."""

        db_user = await self.user_dao.get_by_email(email)

        # Check if invalid credentials
        if not db_user:
            raise InvalidCredentialsError()

        # Map ORM user to domain user
        domain_user = mapper.orm_to_domain(db_user, User)

        # Check if password is correct
        if not domain_user.check_password(password):
            raise InvalidCredentialsError()

        # Create standard JWT access token and hashed opaque refresh token
        access_token = tokens.create_access_token(domain_user.id)
        opaque_token = tokens.create_opaque_token()

        # Hash the opaque token for storage
        hashed_opaque_token = hashing.get_hash(opaque_token)
        db_refresh_token = RefreshTokenModel(
            hashed_token=hashed_opaque_token,
            user_id=domain_user.id,
        )

        # Delete any existing refresh tokens for the user and save the new one
        # This ensures that only one refresh token is valid at a time
        await self.refresh_token_dao.delete_by_user_id(user_id=domain_user.id)
        await self.refresh_token_dao.save(refresh_token=db_refresh_token)

        return TokenPairDTO(access_token=access_token, refresh_token=opaque_token)
