import datetime
import uuid
from enum import StrEnum

from pydantic import BaseModel, Field


class Tokens(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshToken(BaseModel):
    refresh_token: str
    token_type: str = "bearer"


class AccessToken(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"
    PASSWORD_RESET = "password_reset"
    EMAIL_VERIFICATION = "email_verification"


class TokenPayload(BaseModel):
    exp: datetime.datetime
    sub: uuid.UUID
    token_type: TokenType
    nbf: datetime.datetime
    iat: datetime.datetime
    jti: uuid.UUID
    iss: str
    aud: str


class UpdatePassword(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)
