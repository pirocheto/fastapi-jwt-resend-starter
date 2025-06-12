from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.domain.exceptions.user_exceptions import UserAlreadyExistsError
from app.domain.models.user import User
from app.infrastructure.db.dao.user_dao import UserDAO
from app.schemas.user_dto import UserRegisterDTO


class UserService:
    def __init__(self, session: AsyncSession):
        # Initialize any required dependencies, such as DAOs or repositories
        self.dao = UserDAO(session)

    async def register_user(self, dto: UserRegisterDTO) -> User:
        existing_user = await self.dao.get_by_email(dto.email)

        if existing_user:
            raise UserAlreadyExistsError()

        hashed_password = hash_password(dto.password)

        # Create a new User instance
        user = User(email=dto.email, hashed_password=hashed_password)

        # Use DAO to persist the user
        return await self.dao.create_user(user)
