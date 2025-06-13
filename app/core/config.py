import logging
import secrets
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any, Literal, Self

from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    computed_field,
    model_validator,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

root_dir = Path(__file__).resolve().parents[2]


logger = logging.getLogger(__name__)


def parse_cors(v: Any) -> list[str] | str:
    """Parse CORS origins from a string or list of strings."""
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    # Use top level .env file (one level above ./backend/)
    model_config = SettingsConfigDict(
        env_file=root_dir / ".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    # The root directory of the application
    app_dir: Path = root_dir / "app"

    # Secret key to encode/decode JWT tokens
    # This should be kept secret in production
    SECRET_KEY: str = secrets.token_urlsafe(32)

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    # 60 minutes * 24 hours * 7 days = 7 days
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    # The host for the frontend application
    # This is used for emails
    FRONTEND_HOST: str = "http://localhost:5173"

    # The host for documentation and iss in JWT tokens
    BACKEND_HOST: str = "http://localhost:8000"

    # The environment the application is running in
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    # Allow backend to be accessed from given origins
    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        """
        Add the frontend host to the backend CORS origins
        """
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [self.FRONTEND_HOST]

    # The name of the project
    PROJECT_NAME: str

    # The database configuration
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> MultiHostUrl:  # noqa: N802
        """Build the SQLAlchemy database URI from the settings"""
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    DEFAULT_SUPERUSER_EMAIL: EmailStr
    DEFAULT_SUPERUSER_PASSWORD: str

    # The API key for the Resend service
    RESEND_API_KEY: str | None = None

    # The email address to send test emails to
    EMAILS_TEST_RECIPIENT: EmailStr = "test@example.com"

    # The information about the sender of the emails
    EMAILS_FROM_EMAIL: EmailStr | None = None
    EMAILS_FROM_NAME: str | None = None

    @model_validator(mode="after")
    def _set_default_emails_from(self) -> Self:
        if not self.EMAILS_FROM_NAME:
            self.EMAILS_FROM_NAME = self.PROJECT_NAME
        return self

    # The expiration time for the password reset token
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = 24

    # The expiration time for the email verification token
    VERIFICATION_TOKEN_EXPIRE_HOURS: int = 48

    @computed_field  # type: ignore[prop-decorator]
    @property
    def emails_enabled(self) -> bool:
        return bool(self.RESEND_API_KEY and self.EMAILS_FROM_EMAIL)

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        """
        Check if the given secret is set to the default value
        and raise an error if it is.
        """
        if value == "changethis":
            message = (
                f'The value of {var_name} is "changethis", for security, please change it, at least for deployments.'
            )
            if self.ENVIRONMENT == "local":
                logger.warning(message)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        """
        Check if the given secrets are set to the default value
        and raise an error if they are.
        """
        self._check_default_secret("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)
        return self


@lru_cache
def get_settings() -> Settings:
    """
    Get settings with caching
    This is used to avoid reloading the settings
    every time they are accessed.
    """
    return Settings()  # type: ignore


settings = get_settings()
