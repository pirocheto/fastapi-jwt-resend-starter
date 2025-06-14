import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import UserFactory
from tests.utils import fake

pytestmark = [
    pytest.mark.anyio,
    pytest.mark.integration,
]


async def test_forgot_password_success(client: AsyncClient, user_factory: UserFactory, session: AsyncSession) -> None:
    email = fake.email()
    await user_factory.create(email=email)

    response = await client.post("/api/auth/forgot-password", json={"email": email})
    assert response.status_code == 204
