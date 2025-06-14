import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import PasswordResetTokenModel


class PasswordResetTokenDAO:
    """Data Access Object (DAO) for refresh token-related database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, reset_token: PasswordResetTokenModel) -> None:
        """Add a new password reset refresh token to the database."""

        self.session.add(reset_token)

    async def delete_by_user_id(self, user_id: uuid.UUID) -> None:
        """Delete all password reset tokens associated with a specific user ID."""

        statement = delete(PasswordResetTokenModel).where(PasswordResetTokenModel.user_id == user_id)
        await self.session.execute(statement)

    async def get_by_token(self, hashed_token: str) -> PasswordResetTokenModel | None:
        """Retrieve a password reset token by its hashed value."""

        statement = select(PasswordResetTokenModel).where(PasswordResetTokenModel.hashed_token == hashed_token)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()
