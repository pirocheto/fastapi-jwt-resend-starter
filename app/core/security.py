import secrets
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel, ValidationError

from app.core.config import settings

ALGORITHM = "HS256"


class AccessTokenPayload(BaseModel):
    exp: datetime
    sub: uuid.UUID
    nbf: datetime
    iat: datetime
    jti: uuid.UUID
    iss: str
    aud: str


@dataclass
class OpaqueTokenData:
    token: str
    issued_at: datetime
    expires_at: datetime


@dataclass
class JWTokenData:
    token: str


# Hash a password using bcrypt
def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=12)
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password.decode("utf-8")


# Check if the provided password matches the stored password (hashed)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")  # Convert string back to bytes
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(user_id: uuid.UUID) -> JWTokenData:
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    now = datetime.now(UTC)
    expire = now + access_token_expires
    to_encode = {
        # Expiration time
        "exp": expire,
        # Subject of the token, typically a user ID or username
        "sub": str(user_id),
        # Not before time, indicating when the token is valid from
        "nbf": now,
        # Issued at time, indicating when the token was created
        "iat": now,
        # JWT ID, a unique identifier for the token
        "jti": str(uuid.uuid4()),
        # Issuer of the token, typically the backend host
        "iss": settings.BACKEND_HOST,
        # Audience of the token, typically the frontend host
        "aud": settings.FRONTEND_HOST,
    }

    AccessTokenPayload.model_validate(to_encode)
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return JWTokenData(token=encoded_jwt)


def verify_access_token(token: str) -> str | None:
    try:
        decoded_token = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM],
            issuer=settings.BACKEND_HOST,
            audience=settings.FRONTEND_HOST,
        )

        token_data = AccessTokenPayload.model_validate(decoded_token)

        return str(token_data.sub)
    except (InvalidTokenError, ValidationError):
        return None


def _create_opaque_token(expire_delta: timedelta) -> OpaqueTokenData:
    token = secrets.token_urlsafe(64)
    now = datetime.now(UTC)
    expires_at = now + expire_delta
    return OpaqueTokenData(token=token, issued_at=now, expires_at=expires_at)


def create_refresh_token() -> OpaqueTokenData:
    return _create_opaque_token(timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES))


def create_password_reset_token() -> OpaqueTokenData:
    return _create_opaque_token(timedelta(hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS))


def create_email_verification_token() -> OpaqueTokenData:
    return _create_opaque_token(timedelta(hours=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS))
