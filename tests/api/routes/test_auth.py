from unittest.mock import MagicMock

from faker import Faker
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core import messages, security
from app.core.config import settings
from app.schemas.user import UserCreate
from app.services import user_service
from tests.utils.user import create_random_user, user_authentication_headers

fake = Faker("fr_FR")


def test_login_user(client: TestClient, db: Session) -> None:
    password = fake.password()
    user = create_random_user(db=db, password=password)

    r = client.post(
        f"{settings.API_V1_STR}/auth/token",
        data={"username": user.email, "password": password},
    )

    assert r.status_code == status.HTTP_200_OK
    assert "access_token" in r.json()
    assert "refresh_token" in r.json()
    assert r.json()["token_type"] == "bearer"


def test_login_user_invalid_credentials(client: TestClient) -> None:
    email = fake.email()
    password = fake.password()
    r = client.post(
        f"{settings.API_V1_STR}/auth/token",
        data={"username": email, "password": password},
    )

    assert r.status_code == status.HTTP_401_UNAUTHORIZED
    assert r.json() == {"detail": messages.ERROR_INVALID_CREDENTIALS}


def test_login_user_not_verified(client: TestClient, db: Session) -> None:
    password = fake.password()
    user = create_random_user(
        db=db,
        password=password,
        is_verified=False,
    )

    r = client.post(
        f"{settings.API_V1_STR}/auth/token",
        data={"username": user.email, "password": password},
    )

    assert r.status_code == status.HTTP_401_UNAUTHORIZED
    assert r.json() == {"detail": messages.ERROR_EMAIL_NOT_VERIFIED}


def test_refresh_access_token(client: TestClient, db: Session) -> None:
    password = fake.password()
    user = create_random_user(db=db, password=password)

    # First login to get the access token
    login_response = client.post(
        f"{settings.API_V1_STR}/auth/token",
        data={"username": user.email, "password": password},
    )

    assert login_response.status_code == 200
    refresh_token = login_response.json()["refresh_token"]

    r = client.post(
        f"{settings.API_V1_STR}/auth/token/refresh",
        json={"refresh_token": refresh_token},
    )

    assert r.status_code == status.HTTP_200_OK
    assert "access_token" in r.json()


def test_refresh_access_token_invalid(client: TestClient) -> None:
    r = client.post(
        f"{settings.API_V1_STR}/auth/token/refresh",
        json={"refresh_token": "invalid_token"},
    )

    assert r.status_code == status.HTTP_401_UNAUTHORIZED
    assert r.json() == {"detail": messages.ERROR_INVALID_CREDENTIALS}


def test_refresh_access_token_user_not_found(client: TestClient, db: Session) -> None:
    password = fake.password()
    user = create_random_user(db=db, password=password)

    # First login to get the access token
    login_response = client.post(
        f"{settings.API_V1_STR}/auth/token",
        data={"username": user.email, "password": password},
    )
    assert login_response.status_code == 200
    refresh_token = login_response.json()["refresh_token"]

    # Delete the user to simulate user not found
    user_service.delete_user(session=db, db_user=user)

    r = client.post(
        f"{settings.API_V1_STR}/auth/token/refresh",
        json={"refresh_token": refresh_token},
    )

    assert r.status_code == status.HTTP_404_NOT_FOUND
    assert r.json() == {"detail": messages.ERROR_USER_NOT_FOUND}


def test_send_email_reset_password(mocked_send_email: MagicMock, client: TestClient, db: Session) -> None:
    user = create_random_user(db=db)

    r = client.post(
        f"{settings.API_V1_STR}/auth/password/forgot",
        json={"email": user.email},
    )

    assert r.status_code == status.HTTP_200_OK
    assert mocked_send_email.called
    assert r.json() == {"message": messages.SUCCESS_PASSWORD_RESET_LINK_SENT}


def test_update_password_with_token(client: TestClient, db: Session) -> None:
    user = create_random_user(db=db)

    token = security.create_password_reset_token(subject=user.id)
    new_password = fake.password()

    r = client.post(
        f"{settings.API_V1_STR}/auth/password/reset",
        json={"token": token, "new_password": new_password},
    )

    assert r.status_code == 200
    assert r.json() == {"message": messages.SUCCESS_PASSWORD_RESET}

    # Verify the new password works
    r = client.post(
        f"{settings.API_V1_STR}/auth/token",
        data={"username": user.email, "password": new_password},
    )
    assert r.status_code == 200


def test_register_new_user(mocked_send_email: MagicMock, client: TestClient) -> None:
    email = settings.EMAIL_TEST_USER
    username = fake.user_name()
    password = fake.password()
    r = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={
            "email": email,
            "username": username,
            "password": password,
        },
    )

    assert mocked_send_email.called
    assert r.status_code == 201
    assert r.json() == {"message": messages.SUCCESS_USER_REGISTERED}


def test_register_existing_user(client: TestClient) -> None:
    email = settings.EMAIL_TEST_USER
    username = fake.user_name()
    password = fake.password()
    r = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={
            "email": email,
            "username": username,
            "password": password,
        },
    )

    assert r.status_code == status.HTTP_409_CONFLICT
    assert r.json() == {"detail": messages.ERROR_USER_ALREADY_EXISTS}


def test_verify_email(client: TestClient, db: Session) -> None:
    user = create_random_user(db=db, is_verified=False)

    token = security.create_email_verification_token(subject=user.id)
    r = client.get(f"{settings.API_V1_STR}/auth/verify-email?token={token}")

    assert r.status_code == status.HTTP_200_OK


def test_verify_email_already_verified(client: TestClient, db: Session) -> None:
    email = fake.email()
    password = fake.password()
    username = fake.user_name()
    user_in = UserCreate(email=email, username=username, password=password, email_verified=True)
    user = user_service.create_user(session=db, user_create=user_in)

    token = security.create_email_verification_token(subject=user.id)
    r = client.get(f"{settings.API_V1_STR}/auth/verify-email?token={token}")

    assert r.status_code == status.HTTP_400_BAD_REQUEST
    assert r.json() == {"detail": messages.ERROR_EMAIL_ALREADY_VERIFIED}


def test_resend_verificaton_email(mocked_send_email: MagicMock, client: TestClient, db: Session) -> None:
    user = create_random_user(db=db, is_verified=False)

    r = client.post(
        f"{settings.API_V1_STR}/auth/resend-verification",
        json={"email": user.email},
    )

    assert r.status_code == status.HTTP_200_OK
    assert r.json() == {"message": messages.SUCCESS_EMAIL_VERIFICATION_LINK_SENT}
    assert mocked_send_email.called


def test_resend_verification_email_already_verified(mocked_send_email: MagicMock, client: TestClient, db: Session) -> None:
    user = create_random_user(db=db)

    r = client.post(
        f"{settings.API_V1_STR}/auth/resend-verification",
        json={"email": user.email},
    )

    assert r.status_code == status.HTTP_400_BAD_REQUEST
    assert r.json() == {"detail": messages.ERROR_EMAIL_ALREADY_VERIFIED}
    assert not mocked_send_email.called


def test_update_password(client: TestClient, db: Session) -> None:
    password = fake.password()
    new_password = fake.password()
    user = create_random_user(db=db, password=password)

    headers = user_authentication_headers(user_id=user.id)

    r = client.patch(
        f"{settings.API_V1_STR}/auth/password",
        headers=headers,
        json={"new_password": new_password},
    )

    assert r.status_code == status.HTTP_200_OK
    assert r.json() == {"message": messages.SUCCESS_PASSWORD_UPDATED}

    # Verify the new password works
    r = client.post(
        f"{settings.API_V1_STR}/auth/token",
        data={"username": user.email, "password": new_password},
    )
    assert r.status_code == status.HTTP_200_OK
    assert "access_token" in r.json()
