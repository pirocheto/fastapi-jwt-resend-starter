import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from tests.factories import RefreshTokenFactory, UserFactory
from tests.utils import fake


@pytest.mark.integration
def test_refresh_token_success(client: TestClient, user_factory: UserFactory) -> None:
    password = fake.password()
    user = user_factory.create(password=password)

    # First login to get the refresh token
    login_data = {"username": user.email, "password": password}
    response = client.post(f"{settings.API_V1_STR}/auth/token", data=login_data)
    response_data = response.json()

    assert response.status_code == 200
    assert "refresh_token" in response_data["data"]

    refresh_data = {"refresh_token": response_data["data"]["refresh_token"]}
    response = client.post(f"{settings.API_V1_STR}/auth/token/refresh", json=refresh_data)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["status"] == "success"
    assert "access_token" in response_data["data"]
    assert "refresh_token" in response_data["data"]


@pytest.mark.integration
def test_refresh_token_invalid(client: TestClient) -> None:
    refresh_data = {"refresh_token": "invalid_token"}
    response = client.post(f"{settings.API_V1_STR}/auth/token/refresh", json=refresh_data)
    response_data = response.json()

    assert response.status_code == 401
    assert response_data["status"] == "error"
    assert response_data["code"] == "refresh_token_invalid"


@pytest.mark.integration
def test_refresh_token_user_inactive(
    client: TestClient, user_factory: UserFactory, refresh_token_factory: RefreshTokenFactory
) -> None:
    user = user_factory.create(is_active=False)
    db_token = refresh_token_factory.create(user_id=user.id)

    refresh_data = {"refresh_token": db_token.token}
    response = client.post(f"{settings.API_V1_STR}/auth/token/refresh", json=refresh_data)
    response_data = response.json()

    assert response.status_code == 403
    assert response_data["status"] == "error"
    assert response_data["code"] == "user_inactive"


@pytest.mark.integration
def test_refresh_token_email_not_verified(
    client: TestClient, user_factory: UserFactory, refresh_token_factory: RefreshTokenFactory
) -> None:
    user = user_factory.create(email_verified=False)
    db_token = refresh_token_factory.create(user_id=user.id)

    refresh_data = {"refresh_token": db_token.token}
    response = client.post(f"{settings.API_V1_STR}/auth/token/refresh", json=refresh_data)
    response_data = response.json()

    assert response.status_code == 403
    assert response_data["status"] == "error"
    assert response_data["code"] == "email_not_verified"
