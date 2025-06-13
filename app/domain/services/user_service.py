import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions.user_exceptions import UserAlreadyExistsError, UserNotFoundError
from app.domain.models.user import User
from app.domain.models.verification_token import VerificationToken
from app.infrastructure.dao.user_dao import UserDAO
from app.infrastructure.dao.verification_token_dao import VerificationTokenDAO
from app.infrastructure.utils import email_helper, hash_helper, token_helper
from app.mappers.user_mapper import orm_to_domain
from app.schemas.user_dto import UserRegisterDTO


class UserService:
    def __init__(self, session: AsyncSession):
        # Initialize the UserDAO with the provided session
        self.user_dao = UserDAO(session)
        self.verif_token_dao = VerificationTokenDAO(session)

    async def register_user(self, user_in: UserRegisterDTO) -> User:
        """Register a new user."""

        existing_user = await self.user_dao.get_by_email(user_in.email)

        if existing_user:
            raise UserAlreadyExistsError()

        # Prepare the user data for saving, excluding the password field
        user_dict = user_in.model_dump(exclude_unset=True, exclude={"password"})
        user_dict["hashed_password"] = hash_helper.get_hash(user_in.password)

        domain_user = User(**user_dict)
        db_user = await self.user_dao.save(domain_user)

        # Create a verification token for the new user
        opaque_tokon = token_helper.create_opaque_token()
        hashed_opaque_token = hash_helper.get_hash(opaque_tokon)
        domain_verif_token = VerificationToken(user_id=domain_user.id, hashed_token=hashed_opaque_token)

        # Delete any existing verification tokens for the user and save the new one
        await self.verif_token_dao.delete_by_user_id(user_id=domain_user.id)
        await self.verif_token_dao.save(domain_verif_token)

        # Send verification email
        email_helper.generate_verification_email(email_to=domain_user.email, token=opaque_tokon)

        return orm_to_domain(db_user)

    async def get_user_by_id(self, id: uuid.UUID) -> User:
        """Retrieve a user by ID."""

        db_user = await self.user_dao.get_by_id(id)

        if not db_user:
            raise UserNotFoundError()

        return orm_to_domain(db_user)
