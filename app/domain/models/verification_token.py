import uuid
from datetime import datetime, timedelta

from pydantic import BaseModel

from app.core.config import settings


class VerificationToken(BaseModel):
    id: uuid.UUID = uuid.uuid4()
    user_id: uuid.UUID
    hashed_token: str
    created_at: datetime = datetime.now()
    expires_at: datetime = datetime.now() + timedelta(
        hours=settings.VERIFICATION_TOKEN_EXPIRE_HOURS,
    )

    def is_expired(self) -> bool:
        """Check if the verification token is expired."""
        return datetime.now() > self.expires_at
