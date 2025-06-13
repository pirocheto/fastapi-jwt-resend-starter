from fastapi import status

from app.domain.exceptions.base_exceptions import AppError


class InvalidAccessTokenError(AppError):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="invalid_access_token",
            detail="Access token is invalid or expired",
        )


class InvalidCredentialsError(AppError):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="invalid_credentials",
            detail="Invalid email or password",
        )
