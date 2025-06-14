from collections.abc import AsyncGenerator, Generator
from unittest.mock import MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import Base
from app.infrastructure.db.session import engine
from app.main import app
from tests.factories import PasswordResetTokenFactory, UserFactory, VerificationTokenFactory
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
async def session() -> AsyncGenerator[AsyncSession]:
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session


@pytest.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest.fixture(scope="function", autouse=True)
def mocked_send_email() -> Generator[MagicMock]:
    with patch("resend.Emails.send") as mock:
        mock.return_value = {"id": fake.uuid4()}
        yield mock


@pytest.fixture(scope="function")
def user_factory(session: AsyncSession) -> UserFactory:
    return UserFactory(session)


@pytest.fixture(scope="function")
def reset_token_factory(session: AsyncSession) -> PasswordResetTokenFactory:
    return PasswordResetTokenFactory(session)


@pytest.fixture(scope="function")
def verif_token_factory(session: AsyncSession) -> VerificationTokenFactory:
    return VerificationTokenFactory(session)


@pytest.fixture(scope="function")
async def auth_headers(user_factory: UserFactory, client: AsyncClient) -> dict[str, str]:
    password = fake.password()
    user = await user_factory.create(password=password)
    login_data = {"username": user.email, "password": password}
    response = await client.post("/api/auth/login", data=login_data)
    response_data = response.json()

    access_token = response_data["access_token"]
    return {"Authorization": f"Bearer {access_token}"}
