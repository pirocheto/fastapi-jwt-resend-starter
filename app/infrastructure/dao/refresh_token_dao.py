import uuid

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.refresh_token import RefreshToken
from app.infrastructure.db.models import RefreshTokenModel
from app.mappers.refresh_token_mapper import domain_to_orm


class RefreshTokenDAO:
    """Data Access Object (DAO) for refresh token-related database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, refresh_token: RefreshToken) -> RefreshTokenModel:
        """Save a new refresh token to the database."""

        refresh_token_model = domain_to_orm(refresh_token)

        self.session.add(refresh_token_model)
        await self.session.commit()
        await self.session.refresh(refresh_token)
        return refresh_token_model

    async def delete_by_user_id(self, user_id: uuid.UUID) -> None:
        """Delete all refresh tokens associated with a user ID."""

        statement = delete(RefreshTokenModel).where(RefreshTokenModel.user_id == user_id)
        await self.session.execute(statement)
        await self.session.commit()
