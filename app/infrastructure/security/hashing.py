import hashlib
import hmac

import bcrypt

from app.core.config import settings


# Hash a password using bcrypt
def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode()
    salt = bcrypt.gensalt(rounds=12)
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password.decode()


# Check if the provided password matches the stored password (hashed)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode()
    hashed_bytes = hashed_password.encode()  # Convert string back to bytes
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def get_token_hash(token: str) -> str:
    secret_key = settings.SECRET_KEY.encode()
    message = token.encode()
    return hmac.new(secret_key, message, digestmod=hashlib.sha256).hexdigest()
