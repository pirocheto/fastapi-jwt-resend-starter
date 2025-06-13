from pydantic import BaseModel, ConfigDict, Field


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
