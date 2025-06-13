import uuid
from datetime import UTC, datetime, timedelta

from pydantic import BaseModel
from pydantic.networks import EmailStr

from app.core.config import settings
from app.infrastructure.security import hashing


class DomainModel(BaseModel):
    pass


class AccessTokenPayload(DomainModel):
    exp: datetime
    sub: uuid.UUID
    nbf: datetime = datetime.now(UTC)
    iat: datetime = datetime.now(UTC)
    jti: uuid.UUID = uuid.uuid4()
    iss: str = settings.BACKEND_HOST
    aud: str = settings.FRONTEND_HOST

    def is_expired(self) -> bool:
        """Check if the access token is expired."""
        return datetime.now() > self.exp

    def is_valid(self) -> bool:
        """Check if the access token is valid."""
        return not self.is_expired() and self.iss == settings.BACKEND_HOST and self.aud == settings.FRONTEND_HOST


class User(DomainModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID = uuid.uuid4()
    email: EmailStr
    hashed_password: str
    is_verified: bool = False
    created_at: datetime = datetime.now(UTC)
    updated_at: datetime = datetime.now(UTC)

    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the hashed password."""

        return hashing.verify_password(password, self.hashed_password)

    def update_password(self, new_password: str) -> None:
        """Update the user's password."""

        self.hashed_password = hashing.get_password_hash(new_password)
        self.updated_at = datetime.now(UTC)


class RefreshToken(DomainModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID = uuid.uuid4()
    user_id: uuid.UUID
    hashed_token: str
    created_at: datetime = datetime.now(UTC)
    expires_at: datetime = datetime.now(UTC) + timedelta(
        minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES,
    )

    def is_expired(self) -> bool:
        """Check if the refresh token is expired."""
        return datetime.now(UTC) > self.expires_at


class VerificationToken(DomainModel):
    id: uuid.UUID | None = uuid.uuid4()
    user_id: uuid.UUID | None = None
    hashed_token: str
    created_at: datetime = datetime.now(UTC)
    expires_at: datetime = datetime.now(UTC) + timedelta(
        hours=settings.VERIFICATION_TOKEN_EXPIRE_HOURS,
    )

    def is_expired(self) -> bool:
        """Check if the verification token is expired."""
        return datetime.now(UTC) > self.expires_at
