from fastapi import HTTPException, status

from app.core import messages


class CustomHTTPException(HTTPException):
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = "Internal Server Error"

    def __init__(self) -> None:
        super().__init__(status_code=self.status_code, detail=self.detail)


class InvalidCredentialsException(CustomHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = messages.ERROR_INVALID_CREDENTIALS


class UserNotFoundException(CustomHTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = messages.ERROR_USER_NOT_FOUND


class InactiveUserException(CustomHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = messages.ERROR_USER_INACTIVE


class EmailNotVerifiedException(CustomHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = messages.ERROR_EMAIL_NOT_VERIFIED


class UserAlreadyExistsException(CustomHTTPException):
    status_code = status.HTTP_409_CONFLICT
    detail = messages.ERROR_USER_ALREADY_EXISTS


class PasswordResetTokenInvalidException(CustomHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = messages.ERROR_PASSWORD_RESET_TOKEN_INVALID


class VerificationTokenInvalidException(CustomHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = messages.ERROR_VERIFICATION_TOKEN_INVALID


class EmailAlreadyVerifiedException(CustomHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = messages.ERROR_EMAIL_ALREADY_VERIFIED
