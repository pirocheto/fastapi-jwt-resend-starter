from fastapi.testclient import TestClient

from app.core.config import settings
from tests.factories import UserFactory


def test_login_user(client: TestClient, user_factory: UserFactory) -> None:
    password = "defaultpassword"
    user = user_factory.create(password=password)

    data = {"username": user.email, "password": password}
    response = client.post(f"{settings.API_V1_STR}/auth/token", data=data)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["status"] == "success"
    assert "access_token" in response_data["data"]
    assert "refresh_token" in response_data["data"]


def test_refresh_access_token(client: TestClient, user_factory: UserFactory) -> None:
    password = "defaultpassword"
    user = user_factory.create(password=password)

    # First, log in to get the refresh token
    login_data = {"username": user.email, "password": password}
    login_response = client.post(f"{settings.API_V1_STR}/auth/token", data=login_data)
    login_response_data = login_response.json()

    assert login_response.status_code == 200
    assert "refresh_token" in login_response_data["data"]

    refresh_token = login_response_data["data"]["refresh_token"]

    # Now, use the refresh token to get a new access token
    refresh_data = {"refresh_token": refresh_token}
    refresh_response = client.post(f"{settings.API_V1_STR}/auth/token/refresh", json=refresh_data)
    refresh_response_data = refresh_response.json()

    assert refresh_response.status_code == 200
    assert refresh_response_data["status"] == "success"
    assert "access_token" in refresh_response_data["data"]
