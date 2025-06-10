import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    username: str = Field(min_length=3, max_length=255)
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    is_superuser: bool = Field(default=False)
    is_active: bool = Field(default=True)
    email_verified: bool = Field(default=False)


class UserRegister(BaseModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    username: str | None = Field(default=None, max_length=255)


class UserUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    username: str | None = Field(default=None, min_length=3, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=128)
    email_verified: bool | None = Field(default=None)
    is_active: bool | None = Field(default=None)
    is_superuser: bool | None = Field(default=None)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: uuid.UUID
    username: str
    email: EmailStr
    is_superuser: bool
    is_active: bool
    email_verified: bool
