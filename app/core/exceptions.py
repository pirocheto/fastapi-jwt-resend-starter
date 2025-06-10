from fastapi import status


class APIException(Exception):
    def __init__(self, code: str, message: str, status_code: int) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class UserNotFound(APIException):
    def __init__(self) -> None:
        super().__init__(
            code="user_not_found",
            message="User not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class RefreshTokenInvalid(APIException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="refresh_token_invalid",
            message="The refresh token is invalid.",
        )


class RefreshTokenExpired(APIException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="refresh_token_expired",
            message="Refresh token has expired.",
        )


class UserAlreadyExists(APIException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            code="user_already_exists",
            message="A user with this email already exists.",
        )


class InvalidCredentials(APIException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="invalid_credentials",
            message="Incorrect credentials.",
        )


class InvalidAccessToken(APIException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="invalid_access_token",
            message="The access token is invalid or expired.",
        )


class UserInactive(APIException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            code="user_inactive",
            message="The user is inactive.",
        )


class EmailNotVerified(APIException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            code="email_not_verified",
            message="The user's email is not verified.",
        )


class RefreshTokenRevoked(APIException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            code="refresh_token_revoked",
            message="Refresh token has been revoked.",
        )


class RefreshTokenNotFound(APIException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code="refresh_token_not_found",
            message="Refresh token not found.",
        )


class PasswordResetTokenNotFound(APIException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code="password_reset_token_not_found",
            message="Password reset token not found.",
        )


class PasswordResetTokenAlreadyUsed(APIException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="password_reset_token_already_used",
            message="Password reset token has already been used.",
        )


class PasswordIncorrect(APIException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="password_incorrect",
            message="The provided password is incorrect.",
        )


class VerificationTokenNotFound(APIException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code="verification_token_not_found",
            message="Verification token not found.",
        )


class PasswordResetTokenExpired(APIException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="password_reset_token_expired",
            message="Password reset token has expired.",
        )


class VerificationTokenExpired(APIException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="verification_token_expired",
            message="Verification token has expired.",
        )


class EmailAlreadyVerified(APIException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="email_already_verified",
            message="The user's email is already verified.",
        )


class VerificationTokenAlreadyUsed(APIException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="verification_token_already_used",
            message="Verification token has already been used.",
        )
