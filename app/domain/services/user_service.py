import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions.user_exceptions import UserNotFoundError
from app.domain.models import User
from app.infrastructure.dao import UserDAO, VerificationTokenDAO
from app.utils import mapper


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_dao = UserDAO(session)
        self.verif_token_dao = VerificationTokenDAO(session)

    async def get_user_by_id(self, id: uuid.UUID) -> User:
        """Retrieve a user by ID."""

        db_user = await self.user_dao.get_by_id(id)

        if not db_user:
            raise UserNotFoundError()

        return mapper.orm_to_domain(db_user, User)
