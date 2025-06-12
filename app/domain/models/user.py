from datetime import datetime

from pydantic import UUID4, BaseModel, EmailStr


class User(BaseModel):
    id: UUID4 | None = None
    email: EmailStr
    hashed_password: str
    is_verified: bool = False
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __repr__(self) -> str:
        return str(self.model_dump())
