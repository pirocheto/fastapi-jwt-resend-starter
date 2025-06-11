import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from tests.factories import UserFactory


@pytest.mark.integration
def test_get_user_details(client: TestClient, user_factory: UserFactory, auth_headers: dict[str, str]) -> None:
    response = client.get(f"{settings.API_V1_STR}/users/me", headers=auth_headers)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["status"] == "success"
    assert "data" in response_data
    assert "email" in response_data["data"]
    assert "username" in response_data["data"]
