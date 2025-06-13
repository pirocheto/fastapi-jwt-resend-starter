import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: uuid.UUID = uuid.uuid4()
    email: EmailStr
    hashed_password: str
    is_verified: bool = False
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
