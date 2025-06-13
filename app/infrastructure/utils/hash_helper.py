import bcrypt


# Hash a password using bcrypt
def get_hash(value: str) -> str:
    pwd_bytes = value.encode()
    salt = bcrypt.gensalt(rounds=12)
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password.decode()


# Check if the provided password matches the stored password (hashed)
def check_hash(plain_value: str, hashed_value: str) -> bool:
    password_bytes = plain_value.encode()
    hashed_bytes = hashed_value.encode()  # Convert string back to bytes
    return bcrypt.checkpw(password_bytes, hashed_bytes)
