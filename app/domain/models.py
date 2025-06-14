import uuid
from datetime import UTC, datetime, timedelta

from pydantic import BaseModel, ConfigDict
from pydantic.networks import EmailStr

from app.core.config import settings


class DomainModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class User(DomainModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = uuid.uuid4()
    email: EmailStr
    hashed_password: str
    is_verified: bool = False
    created_at: datetime = datetime.now(UTC)
    updated_at: datetime = datetime.now(UTC)


class RefreshToken(DomainModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = uuid.uuid4()
    user_id: uuid.UUID
    hashed_token: str
    created_at: datetime = datetime.now(UTC)
    expires_at: datetime = datetime.now(UTC) + timedelta(
        minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES,
    )


class VerificationToken(DomainModel):
    id: uuid.UUID | None = uuid.uuid4()
    user_id: uuid.UUID | None = None
    hashed_token: str
    created_at: datetime = datetime.now(UTC)
    expires_at: datetime = datetime.now(UTC) + timedelta(
        hours=settings.VERIFICATION_TOKEN_EXPIRE_HOURS,
    )


class PasswordResetToken(DomainModel):
    id: uuid.UUID = uuid.uuid4()
    user_id: uuid.UUID
    hashed_token: str
    created_at: datetime = datetime.now(UTC)
    expires_at: datetime = datetime.now(UTC) + timedelta(
        hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS,
    )
