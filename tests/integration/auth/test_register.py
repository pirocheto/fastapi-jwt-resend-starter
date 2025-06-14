import pytest
from httpx import AsyncClient

from tests.utils import fake

pytestmark = [
    pytest.mark.anyio,
    pytest.mark.integration,
]


async def test_register_new_user_success(client: AsyncClient) -> None:
    register_data = {
        "email": fake.email(),
        "password": fake.password(),
    }
    response = await client.post("api/auth/register", json=register_data)
    response_data = response.json()

    assert response.status_code == 201
    assert "id" in response_data
    assert response_data["email"] == register_data["email"]
