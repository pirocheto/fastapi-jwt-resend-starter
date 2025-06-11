import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from tests.factories import UserFactory
from tests.utils import fake


@pytest.mark.integration
def test_update_password_with_inactive_user(client: TestClient, user_factory: UserFactory) -> None:
    user = user_factory.create(is_active=False)

    reset_data = {"email": user.email}
    response = client.post(f"{settings.API_V1_STR}/auth/password/forgot", json=reset_data)
    response_data = response.json()

    assert response.status_code == 403
    assert response_data["status"] == "error"
    assert response_data["code"] == "user_inactive"


@pytest.mark.integration
def test_update_password_success(client: TestClient, user_factory: UserFactory) -> None:
    password = fake.password()
    user = user_factory.create(password=password)

    # First login to get the access token
    login_data = {"username": user.email, "password": password}
    response = client.post(f"{settings.API_V1_STR}/auth/token", data=login_data)
    response_data = response.json()

    assert response.status_code == 200
    assert "access_token" in response_data["data"]

    # Update the password
    update_data = {"current_password": password, "new_password": fake.password()}
    headers = {"Authorization": f"Bearer {response_data['data']['access_token']}"}
    response = client.patch(f"{settings.API_V1_STR}/auth/password", json=update_data, headers=headers)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["status"] == "success"
    assert response_data["code"] == "password_updated"


@pytest.mark.integration
def test_update_password_invalid_current_password(client: TestClient, auth_headers: dict[str, str]) -> None:
    update_data = {"current_password": "wrongpassword", "new_password": fake.password()}
    response = client.patch(f"{settings.API_V1_STR}/auth/password", json=update_data, headers=auth_headers)
    response_data = response.json()

    assert response.status_code == 401
    assert response_data["status"] == "error"
    assert response_data["code"] == "password_incorrect"


@pytest.mark.integration
def test_update_password_unauthenticated(client: TestClient) -> None:
    update_data = {"current_password": "oldpassword", "new_password": "newpassword"}
    response = client.patch(f"{settings.API_V1_STR}/auth/password", json=update_data)
    response_data = response.json()

    assert response.status_code == 401
    assert response_data["status"] == "error"
    assert response_data["code"] == "not_authenticated"
