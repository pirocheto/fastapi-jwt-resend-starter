from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import engine
from app.main import app
from app.models import Base
from tests.factories import EmailVerificationTokenFactory, PasswordResetTokenFactory, RefreshTokenFactory, UserFactory
from tests.utils import fake


@pytest.fixture(scope="session", autouse=True)
def create_test_database() -> Generator[None]:
    Base.metadata.create_all(bind=engine)
    yield
    # Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def session() -> Generator[Session]:
    with Session(engine) as session:
        yield session


@pytest.fixture(scope="function")
def user_factory(session: Session) -> UserFactory:
    return UserFactory(session)


@pytest.fixture(scope="function")
def password_refresh_token_factory(session: Session) -> RefreshTokenFactory:
    return RefreshTokenFactory(session)


@pytest.fixture(scope="function")
def password_reset_token_factory(session: Session) -> PasswordResetTokenFactory:
    return PasswordResetTokenFactory(session)


@pytest.fixture(scope="function")
def email_verification_token_factory(session: Session) -> EmailVerificationTokenFactory:
    return EmailVerificationTokenFactory(session)


@pytest.fixture(scope="function")
def refresh_token_factory(session: Session) -> RefreshTokenFactory:
    return RefreshTokenFactory(session)


@pytest.fixture(scope="function")
def client() -> Generator[TestClient]:
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function", autouse=True)
def mocked_send_email() -> Generator[MagicMock]:
    with patch("resend.Emails.send") as mock:
        mock.return_value = {"id": fake.uuid4()}
        yield mock


@pytest.fixture(scope="function")
def auth_headers(user_factory: UserFactory, client: TestClient) -> dict[str, str]:
    password = fake.password()
    user = user_factory.create(password=password)
    login_data = {"username": user.email, "password": password}
    response = client.post(f"{settings.API_V1_STR}/auth/token", data=login_data)
    response_data = response.json()

    access_token = response_data["access_token"]
    return {"Authorization": f"Bearer {access_token}"}
