from datetime import datetime

from pydantic import UUID4, BaseModel, ConfigDict, EmailStr, Field


class UserRegister(BaseModel):
    """Model for user registration."""

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, max_length=64, description="Secure password")

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "password": "strongpassword123",
            }
        }
    }


class UserRegisterResponse(BaseModel):
    """Response model for user registration."""

    id: UUID4 = Field(..., description="Unique identifier for the user (UUIDv4)")
    email: EmailStr = Field(..., description="User's email address")
    created_at: datetime = Field(..., description="Account creation timestamp (ISO 8601 format)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "created_at": "2024-06-01T12:34:56Z",
            }
        }
    }


class TokenPair(BaseModel):
    """Pair of access and refresh tokens."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="Opaque refresh token")
    type: str = Field(
        default="Bearer",
        description="Token type, typically 'Bearer' for access tokens",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": (
                    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
                    "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ."
                    "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
                ),
                "refresh_token": ("dGhpc2lzYXJlZnJlc2h0b2tlbmZvcmV4YW1wbGUu" "MTIzNDU2Nzg5MA"),
            }
        }
    )


class RefreshAccessTokenRequest(BaseModel):
    """Request model for refreshing access token."""

    refresh_token: str = Field(..., description="Opaque refresh token to be used for refreshing the access token")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "refresh_token": "dGhpc2lzYXJlZnJlc2h0b2tlbmZvcmV4YW1wbGUuMTIzNDU2Nzg5MA",
            }
        }
    )


class ForgotPasswordRequest(BaseModel):
    """Request model for forgot password functionality."""

    email: EmailStr = Field(..., description="Email address of the user requesting password reset")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"email": "user@example.com"},
        }
    )


class ResetPasswordRequest(BaseModel):
    """Request model for resetting user password."""

    token: str = Field(..., description="Opaque token for password reset")
    new_password: str = Field(..., min_length=8, max_length=64, description="New secure password")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "token": "dGhpc2lzYXJlZnJlc2h0b2tlbmZvcmV4YW1wbGUuMTIzNDU2Nzg5MA",
                "new_password": "newstrongpassword123",
            }
        }
    )


class VerifyEmailRequest(BaseModel):
    """Request model for verifying user email."""

    token: str = Field(..., description="Verification token sent to the user's email")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "token": "dGhpc2lzYXJlZnZlcmlmaWNhdGlvbnRva2VuMTIzNDU2Nzg5MA",
            }
        }
    )


class ResendVerifEmailRequest(BaseModel):
    """Request model for resending verification link to user's email."""

    email: EmailStr = Field(..., description="Email address of the user to resend verification link")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"email": "user@example.com"},
        }
    )
