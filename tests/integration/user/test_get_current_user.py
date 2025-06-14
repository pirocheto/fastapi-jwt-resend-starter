import pytest
from httpx import AsyncClient

pytestmark = [
    pytest.mark.anyio,
    pytest.mark.integration,
]


async def test_get_current_user_success(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    response = await client.get("/api/users/me", headers=auth_headers)
    response_data = response.json()

    assert response.status_code == 200
    assert "id" in response_data
    assert "email" in response_data
