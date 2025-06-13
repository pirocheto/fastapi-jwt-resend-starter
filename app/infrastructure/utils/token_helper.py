import secrets
import uuid
from datetime import datetime, timedelta
from typing import Any

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from app.core.config import settings
from app.domain.models.access_token import AccessTokenPayload

ALGORITHM = "HS256"


def create_access_token(subject: Any) -> str:
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    now = datetime.now()
    expire = now + access_token_expires
    payload = {
        # Expiration time
        "exp": expire,
        # Subject of the token, typically a user ID or username
        "sub": str(subject),
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

    AccessTokenPayload.model_validate(payload)
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)
    return token


def decode_access_token(token: str) -> AccessTokenPayload | None:
    try:
        decoded_token = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM],
            issuer=settings.BACKEND_HOST,
            audience=settings.FRONTEND_HOST,
        )
        return AccessTokenPayload.model_validate(decoded_token)

    except (ExpiredSignatureError, InvalidTokenError):
        return None


def create_opaque_token() -> str:
    return secrets.token_urlsafe(64)
