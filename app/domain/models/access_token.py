import uuid
from datetime import datetime

from pydantic import BaseModel

from app.core.config import settings


class AccessTokenPayload(BaseModel):
    exp: datetime
    sub: uuid.UUID
    nbf: datetime = datetime.now()
    iat: datetime = datetime.now()
    jti: uuid.UUID = uuid.uuid4()
    iss: str = settings.BACKEND_HOST
    aud: str = settings.FRONTEND_HOST

    def is_expired(self) -> bool:
        """Check if the access token is expired."""
        return datetime.now() > self.exp

    def is_valid(self) -> bool:
        """Check if the access token is valid."""
        return not self.is_expired() and self.iss == settings.BACKEND_HOST and self.aud == settings.FRONTEND_HOST
