import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.domain.models.user import User
from app.infrastructure.db.models import UserModel
from app.mappers.user_mapper import domain_to_orm


class UserDAO:
    """Data Access Object (DAO) for user-related database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> UserModel | None:
        """Retrieve a user by email."""

        statement = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_id(self, id: uuid.UUID) -> UserModel | None:
        """Retrieve a user by ID."""

        statement = select(UserModel).where(UserModel.id == id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def save(self, user: User) -> UserModel:
        """Save a new user to the database."""

        db_model = domain_to_orm(user)

        self.session.add(db_model)
        await self.session.commit()
        await self.session.refresh(db_model)

        return db_model
