import uuid

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import VerificationTokenModel


class VerificationTokenDAO:
    """Data Access Object (DAO) for refresh token-related database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, verif_token: VerificationTokenModel) -> None:
        """Add a new verification token to the database."""

        self.session.add(verif_token)

    async def delete_by_user_id(self, user_id: uuid.UUID) -> None:
        """Delete all refresh tokens associated with a user ID."""

        statement = delete(VerificationTokenModel).where(VerificationTokenModel.user_id == user_id)
        await self.session.execute(statement)
