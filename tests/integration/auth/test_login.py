import pytest
from httpx import AsyncClient

from tests.factories import UserFactory
from tests.utils import fake

pytestmark = [
    pytest.mark.anyio,
    pytest.mark.integration,
]


async def test_login_success(client: AsyncClient, user_factory: UserFactory) -> None:
    password = fake.password()
    user = await user_factory.create(password=password)

    login_data = {
        "username": user.email,
        "password": password,
    }

    response = await client.post("api/auth/login", data=login_data)
    response_data = response.json()

    assert response.status_code == 200
    assert "access_token" in response_data
    assert "refresh_token" in response_data
