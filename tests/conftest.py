from collections.abc import AsyncGenerator, Generator
from unittest.mock import MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import engine
from app.main import app
from app.models import Base
from tests.factories import EmailVerificationTokenFactory, PasswordResetTokenFactory, RefreshTokenFactory, UserFactory
from tests.utils import fake


@pytest.fixture(scope="session", autouse=True)
async def create_test_database() -> AsyncGenerator[None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="function")
async def async_session() -> AsyncGenerator[AsyncSession]:
    async with AsyncSession(engine) as async_session:
        yield async_session
        # await async_session.rollback()


@pytest.fixture(scope="function")
async def async_client() -> AsyncGenerator[AsyncClient]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest.fixture(scope="function")
def user_factory(async_session: AsyncSession) -> UserFactory:
    return UserFactory(async_session)


@pytest.fixture(scope="function")
def password_reset_token_factory(async_session: AsyncSession) -> PasswordResetTokenFactory:
    return PasswordResetTokenFactory(async_session)


@pytest.fixture(scope="function")
def email_verification_token_factory(async_session: AsyncSession) -> EmailVerificationTokenFactory:
    return EmailVerificationTokenFactory(async_session)


@pytest.fixture(scope="function")
def refresh_token_factory(async_session: AsyncSession) -> RefreshTokenFactory:
    return RefreshTokenFactory(async_session)


@pytest.fixture(scope="function", autouse=True)
def mocked_send_email() -> Generator[MagicMock]:
    with patch("resend.Emails.send") as mock:
        mock.return_value = {"id": fake.uuid4()}
        yield mock


@pytest.fixture(scope="function")
async def auth_headers(user_factory: UserFactory, async_client: AsyncClient) -> dict[str, str]:
    password = fake.password()
    user = await user_factory.create(password=password)
    login_data = {"username": user.email, "password": password}
    response = await async_client.post(f"{settings.API_V1_STR}/auth/token", data=login_data)
    response_data = response.json()

    access_token = response_data["access_token"]
    return {"Authorization": f"Bearer {access_token}"}
