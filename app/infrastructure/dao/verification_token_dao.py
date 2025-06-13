import uuid

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.verification_token import VerificationToken
from app.infrastructure.db.models import VerificationTokenModel
from app.mappers import verification_token_mapper


class VerificationTokenDAO:
    """Data Access Object (DAO) for refresh token-related database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, verification_token: VerificationToken) -> VerificationTokenModel:
        """Save a new refresh token to the database."""

        db_verification_token = verification_token_mapper.domain_to_orm(verification_token)

        self.session.add(db_verification_token)
        await self.session.commit()
        await self.session.refresh(db_verification_token)
        return db_verification_token

    async def delete_by_user_id(self, user_id: uuid.UUID) -> None:
        """Delete all refresh tokens associated with a user ID."""

        statement = delete(VerificationTokenModel).where(VerificationTokenModel.user_id == user_id)
        await self.session.execute(statement)
        await self.session.commit()
