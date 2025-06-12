import uuid

from pydantic import BaseModel, EmailStr, Field


class UserRegisterDTO(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, max_length=64, description="Secure password")

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "strongpassword123",
            }
        }


class UserRegisterResponseDTO(BaseModel):
    id: uuid.UUID = Field(..., description="Unique identifier for the user")
    email: EmailStr = Field(..., description="User's email address")
    message: str = Field(..., description="Success message after registration")

    class Config:
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "message": "User registered successfully",
            }
        }
