from fastapi import status

from app.domain.exceptions.base_exceptions import AppError


class UserAlreadyExistsError(AppError):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            code="user_already_exists",
            detail="User with this email already exists",
        )


class UserNotFoundError(AppError):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code="user_not_found",
            detail="User not found",
        )
