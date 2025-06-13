from pydantic import UUID4, BaseModel, EmailStr, Field


class UserRegister(BaseModel):
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


class UserDetail(BaseModel):
    id: UUID4 = Field(..., description="Unique identifier for the user (UUIDv4)")
    email: EmailStr = Field(..., description="User's email address")
    created_at: str = Field(..., description="Account creation timestamp (ISO 8601 format)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "created_at": "2024-06-01T12:34:56Z",
            }
        }
    }


class UserRegisterResponse(BaseModel):
    """Response model for user registration."""

    user: UserDetail = Field(..., description="Details of the registered user")

    model_config = {
        "json_schema_extra": {
            "example": {
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "user@example.com",
                    "created_at": "2024-06-01T12:34:56Z",
                }
            }
        }
    }
