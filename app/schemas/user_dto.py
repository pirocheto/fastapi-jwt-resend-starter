from pydantic import UUID4, BaseModel, ConfigDict, EmailStr, Field


class UserRegisterDTO(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, max_length=64, description="Secure password")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "strongpassword123",
            }
        }
    )


class UserRegisterResponseDTO(BaseModel):
    id: UUID4 = Field(..., description="Unique identifier for the user (UUIDv4)")
    email: EmailStr = Field(..., description="User's email address")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
            }
        }
    )


class UserMeResponseDTO(BaseModel):
    id: UUID4 = Field(..., description="Unique identifier for the user (UUIDv4)")
    email: EmailStr = Field(..., description="User's email address")
    created_at: str = Field(..., description="Account creation timestamp (ISO 8601 format)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "created_at": "2024-06-01T12:34:56Z",
            }
        }
    )
