import uuid
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError

from app.core.config import settings
from app.schemas.auth import TokenPayload, TokenType

ALGORITHM = "HS256"


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


def _create_token(subject: uuid.UUID, token_type: TokenType, expires_delta: timedelta) -> str:
    now = datetime.now(UTC)
    expire = now + expires_delta
    to_encode = {
        # Expiration time
        "exp": expire,
        # Subject of the token, typically a user ID or username
        "sub": str(subject),
        # Type of the token (e.g., access, refresh, password reset, email verification)
        "token_type": token_type,
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

    TokenPayload.model_validate(to_encode)
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_access_token(subject: uuid.UUID) -> str:
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return _create_token(subject, TokenType.ACCESS, access_token_expires)


def create_refresh_token(subject: uuid.UUID) -> str:
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    return _create_token(subject, TokenType.REFRESH, refresh_token_expires)


def create_password_reset_token(subject: uuid.UUID) -> str:
    reset_token_expires = timedelta(hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS)
    return _create_token(subject, TokenType.PASSWORD_RESET, reset_token_expires)


def create_email_verification_token(subject: uuid.UUID) -> str:
    email_verification_expires = timedelta(hours=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS)
    return _create_token(subject, TokenType.EMAIL_VERIFICATION, email_verification_expires)


def _verify_token(token: str, token_type: TokenType) -> str | None:
    try:
        decoded_token = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM],
            issuer=settings.BACKEND_HOST,
            audience=settings.FRONTEND_HOST,
        )
        if decoded_token.get("token_type") != token_type:
            return None

        token_data = TokenPayload.model_validate(decoded_token)

        return str(token_data.sub)
    except (InvalidTokenError, ValidationError):
        return None


def verify_access_token(*, token: str) -> str | None:
    return _verify_token(token, token_type=TokenType.ACCESS)


def verify_refresh_token(*, token: str) -> str | None:
    return _verify_token(token, token_type=TokenType.REFRESH)


def verify_password_reset_token(*, token: str) -> str | None:
    return _verify_token(token, token_type=TokenType.PASSWORD_RESET)


def verify_email_verification_token(*, token: str) -> str | None:
    return _verify_token(token, token_type=TokenType.EMAIL_VERIFICATION)
