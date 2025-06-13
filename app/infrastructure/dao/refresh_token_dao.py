import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import RefreshTokenModel


class RefreshTokenDAO:
    """Data Access Object (DAO) for refresh token-related database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, refresh_token: RefreshTokenModel) -> None:
        """Add a new refresh token to the database."""

        self.session.add(refresh_token)

    async def delete_by_user_id(self, user_id: uuid.UUID) -> None:
        """Delete all refresh tokens associated with a specific user ID."""

        statement = delete(RefreshTokenModel).where(RefreshTokenModel.user_id == user_id)
        await self.session.execute(statement)

    async def get_by_token(self, hashed_token: str) -> RefreshTokenModel | None:
        """Retrieve a refresh token by its hashed value."""

        statement = select(RefreshTokenModel).where(RefreshTokenModel.hashed_token == hashed_token)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()
