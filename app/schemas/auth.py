from pydantic import BaseModel, EmailStr, Field


class AccessTokenRefresh(BaseModel):
    refresh_token: str


class PasswordUpdateToken(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)


class PasswordUpdate(BaseModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


class PasswordReset(BaseModel):
    email: EmailStr


class VerificationResend(BaseModel):
    email: EmailStr


class Tokens(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
