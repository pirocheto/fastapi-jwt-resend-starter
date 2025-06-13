from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions.auth_exceptions import InvalidCredentialsError
from app.domain.models.refresh_token import RefreshToken
from app.infrastructure.dao.refresh_token_dao import RefreshTokenDAO
from app.infrastructure.dao.user_dao import UserDAO
from app.infrastructure.utils.hash_helper import check_hash, get_hash
from app.infrastructure.utils.token_helper import create_access_token, create_opaque_token
from app.mappers import user_mapper
from app.schemas.auth_dto import TokenPairDTO


class AuthService:
    def __init__(self, session: AsyncSession):
        # Initialize DAOs
        self.user_dao = UserDAO(session)
        self.refresh_token_dao = RefreshTokenDAO(session)

    async def login(self, email: str, password: str) -> TokenPairDTO:
        """Authenticate user and return access and refresh tokens."""

        db_user = await self.user_dao.get_by_email(email)

        # Check if invalid credentials
        if not db_user or not check_hash(password, db_user.hashed_password):
            raise InvalidCredentialsError()

        domaain_user = user_mapper.orm_to_domain(db_user)

        # Create standard JWT access token (stateless)
        access_token = create_access_token(subject=domaain_user.id)

        # Create hashed opaque refresh token
        opaque_token = create_opaque_token()
        hashed_opaque_token = get_hash(opaque_token)

        # Create a new RefreshToken object
        refresh_token_obj = RefreshToken(hashed_token=hashed_opaque_token, user_id=domaain_user.id)

        # Delete any existing refresh tokens for the user and save the new one
        # This ensures that only one refresh token is valid at a time
        await self.refresh_token_dao.delete_by_user_id(user_id=domaain_user.id)
        await self.refresh_token_dao.save(refresh_token=refresh_token_obj)

        return TokenPairDTO(access_token=access_token, refresh_token=opaque_token)
