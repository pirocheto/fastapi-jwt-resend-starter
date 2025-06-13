import uuid

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import RefreshTokenModel


class RefreshTokenDAO:
    """Data Access Object (DAO) for refresh token-related database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, refresh_token: RefreshTokenModel) -> None:
        self.session.add(refresh_token)

    async def delete_by_user_id(self, user_id: uuid.UUID) -> None:
        statement = delete(RefreshTokenModel).where(RefreshTokenModel.user_id == user_id)
        await self.session.execute(statement)
