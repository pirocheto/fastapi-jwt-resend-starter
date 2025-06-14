import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import UserFactory
from tests.utils import fake

pytestmark = [
    pytest.mark.anyio,
    pytest.mark.integration,
]


async def test_refresh_token_success(client: AsyncClient, user_factory: UserFactory, session: AsyncSession) -> None:
    password = fake.password()
    user = await user_factory.create(password=password)

    # First login to get the refresh token
    login_data = {"username": user.email, "password": password}
    response = await client.post("/api/auth/login", data=login_data)
    response_data = response.json()

    assert response.status_code == 200
    assert "refresh_token" in response_data

    refresh_data = {"refresh_token": response_data["refresh_token"]}
    response = await client.post("/api/auth/refresh", json=refresh_data)
    response_data = response.json()

    assert response.status_code == 200
    assert "access_token" in response_data
    assert "refresh_token" in response_data
