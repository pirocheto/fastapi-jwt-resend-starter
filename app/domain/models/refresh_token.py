import uuid
from datetime import datetime, timedelta

from pydantic import BaseModel

from app.core.config import settings


class RefreshToken(BaseModel):
    id: uuid.UUID = uuid.uuid4()
    user_id: uuid.UUID
    hashed_token: str
    created_at: datetime = datetime.now()
    expires_at: datetime = datetime.now() + timedelta(
        minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES,
    )

    def is_expired(self) -> bool:
        """Check if the refresh token is expired."""
        return datetime.now() > self.expires_at
