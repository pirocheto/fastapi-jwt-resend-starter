from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.domain.models.user import User
from app.infrastructure.db.models.user_model import UserModel
from app.mappers.user_mapper import orm_to_domain


class UserDAO:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        """Retrieve a user by email."""

        statement = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(statement)
        user_model = result.scalar_one_or_none()

        return orm_to_domain(user_model) if user_model else None

    async def create_user(self, user: User) -> User:
        """Create a new user in the database."""

        user_model = UserModel(user)
        self.session.add(user_model)
        await self.session.commit()
        await self.session.refresh(user_model)

        return orm_to_domain(user_model)
