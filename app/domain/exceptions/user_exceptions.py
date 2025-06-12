from fastapi import status

from app.domain.exceptions.base_exceptions import ApplicationError


class UserAlreadyExistsError(ApplicationError):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            code="user_already_exists",
            detail="User with this email already exists",
        )
