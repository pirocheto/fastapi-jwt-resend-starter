import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions.user_exceptions import UserAlreadyExistsError, UserNotFoundError
from app.domain.models.user import User
from app.infrastructure.dao.user_dao import UserDAO
from app.infrastructure.utils import hash_helper
from app.mappers.user_mapper import orm_to_domain
from app.schemas.user_dto import UserRegisterDTO


class UserService:
    def __init__(self, session: AsyncSession):
        # Initialize the UserDAO with the provided session
        self.user_dao = UserDAO(session)

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

        return orm_to_domain(db_user)

    async def get_user_by_id(self, id: uuid.UUID) -> User:
        """Retrieve a user by ID."""

        domain_user = await self.user_dao.get_by_id(id)

        if not domain_user:
            raise UserNotFoundError()

        return orm_to_domain(domain_user)
