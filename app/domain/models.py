import uuid
from datetime import datetime, timedelta

from pydantic import BaseModel
from pydantic.networks import EmailStr

from app.core.config import settings
from app.infrastructure.security import hashing


class DomainModel(BaseModel):
    pass


class AccessTokenPayload(DomainModel):
    exp: datetime
    sub: uuid.UUID
    nbf: datetime = datetime.now()
    iat: datetime = datetime.now()
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
    id: uuid.UUID = uuid.uuid4()
    email: EmailStr
    hashed_password: str
    is_verified: bool = False
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the hashed password."""

        return hashing.check_hash(password, self.hashed_password)

    def update_password(self, new_password: str) -> None:
        """Update the user's password."""

        self.hashed_password = hashing.get_hash(new_password)
        self.updated_at = datetime.now()


class RefreshToken(DomainModel):
    id: uuid.UUID = uuid.uuid4()
    user_id: uuid.UUID
    hashed_token: str
    created_at: datetime = datetime.now()
    expires_at: datetime = datetime.now() + timedelta(
        minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES,
    )

    def is_expired(self) -> bool:
        """Check if the refresh token is expired."""
        return datetime.now() > self.expires_at


class VerificationToken(DomainModel):
    id: uuid.UUID = uuid.uuid4()
    user_id: uuid.UUID
    hashed_token: str
    created_at: datetime = datetime.now()
    expires_at: datetime = datetime.now() + timedelta(
        hours=settings.VERIFICATION_TOKEN_EXPIRE_HOURS,
    )

    def is_expired(self) -> bool:
        """Check if the verification token is expired."""
        return datetime.now() > self.expires_at
