import pytest
from httpx import AsyncClient

from app.core.config import settings

pytestmark = [
    pytest.mark.anyio,
    pytest.mark.integration,
]


async def test_get_user_details(async_client: AsyncClient, auth_headers: dict[str, str]) -> None:
    response = await async_client.get(f"{settings.API_V1_STR}/users/me", headers=auth_headers)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["status"] == "success"
    assert "data" in response_data
    assert "email" in response_data["data"]
    assert "username" in response_data["data"]
