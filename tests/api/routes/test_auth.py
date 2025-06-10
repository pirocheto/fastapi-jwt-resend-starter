from unittest.mock import MagicMock

from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from starlette import status

from app.core.config import settings
from app.schemas.user import UserUpdate
from app.services import token_service, user_service
from tests.utils.user import create_random_user, user_authentication_headers

fake = Faker("fr_FR")


# ===========================================
# AUTHENTICATION: LOGIN
# ===========================================


def test_login_user(client: TestClient, db: Session) -> None:
    password = fake.password()
    user = create_random_user(db=db, password=password)

    r = client.post(
        f"{settings.API_V1_STR}/auth/token",
        data={"username": user.email, "password": password},
    )

    assert r.status_code == status.HTTP_200_OK


def test_login_user_invalid_credentials(client: TestClient) -> None:
    email = fake.email()
    password = fake.password()

    r = client.post(
        f"{settings.API_V1_STR}/auth/token",
        data={"username": email, "password": password},
    )

    assert r.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_user_not_verified(client: TestClient, db: Session) -> None:
    password = fake.password()
    user = create_random_user(db=db, password=password, email_verified=False)

    r = client.post(
        f"{settings.API_V1_STR}/auth/token",
        data={"username": user.email, "password": password},
    )

    assert r.status_code == status.HTTP_403_FORBIDDEN


# ===========================================
# AUTHENTICATION: REFRESH TOKEN
# ===========================================


def test_refresh_access_token(client: TestClient, db: Session) -> None:
    password = fake.password()
    user = create_random_user(db=db, password=password)

    login_response = client.post(
        f"{settings.API_V1_STR}/auth/token",
        data={"username": user.email, "password": password},
    )
    r_data = login_response.json()
    refresh_token = r_data["data"]["refresh_token"]

    r = client.post(
        f"{settings.API_V1_STR}/auth/token/refresh",
        json={"refresh_token": refresh_token},
    )

    assert r.status_code == status.HTTP_200_OK


def test_refresh_access_token_invalid(client: TestClient) -> None:
    r = client.post(
        f"{settings.API_V1_STR}/auth/token/refresh",
        json={"refresh_token": "invalid_token"},
    )
    assert r.status_code == status.HTTP_401_UNAUTHORIZED


def test_refresh_access_token_user_not_found(client: TestClient, db: Session) -> None:
    password = fake.password()
    user = create_random_user(db=db, password=password)

    login_response = client.post(
        f"{settings.API_V1_STR}/auth/token",
        data={"username": user.email, "password": password},
    )
    r_data = login_response.json()
    refresh_token = r_data["data"]["refresh_token"]

    user_service.delete_user(session=db, db_user=user)

    r = client.post(
        f"{settings.API_V1_STR}/auth/token/refresh",
        json={"refresh_token": refresh_token},
    )

    assert r.status_code == status.HTTP_401_UNAUTHORIZED


# ===========================================
# PASSWORD RESET
# ===========================================


def test_send_email_reset_password(mocked_send_email: MagicMock, client: TestClient, db: Session) -> None:
    user = create_random_user(db=db)

    r = client.post(
        f"{settings.API_V1_STR}/auth/password/forgot",
        json={"email": user.email},
    )

    assert r.status_code == status.HTTP_200_OK
    assert mocked_send_email.called


def test_update_password_with_token(client: TestClient, db: Session) -> None:
    db_user = create_random_user(db=db)
    db_token = token_service.create_password_reset_token(session=db, db_user=db_user)
    new_password = fake.password()

    r = client.post(
        f"{settings.API_V1_STR}/auth/password/reset",
        json={"token": db_token.token, "new_password": new_password},
    )

    assert r.status_code == status.HTTP_200_OK

    r = client.post(
        f"{settings.API_V1_STR}/auth/token",
        data={"username": db_user.email, "password": new_password},
    )

    assert r.status_code == status.HTTP_200_OK


def test_update_password(client: TestClient, db: Session) -> None:
    password = fake.password()
    new_password = fake.password()
    user = create_random_user(db=db, password=password)
    headers = user_authentication_headers(db_user=user)

    r = client.patch(
        f"{settings.API_V1_STR}/auth/password",
        headers=headers,
        json={"current_password": password, "new_password": new_password},
    )

    assert r.status_code == status.HTTP_200_OK

    login = client.post(
        f"{settings.API_V1_STR}/auth/token",
        data={"username": user.email, "password": new_password},
    )
    assert login.status_code == status.HTTP_200_OK


# ===========================================
# USER REGISTRATION
# ===========================================


def test_register_new_user(mocked_send_email: MagicMock, client: TestClient) -> None:
    email = fake.email()
    username = fake.user_name()
    password = fake.password()

    r = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": email, "username": username, "password": password},
    )

    assert r.status_code == status.HTTP_201_CREATED


def test_register_existing_user(
    client: TestClient,
    db: Session,
) -> None:
    password = fake.password()
    user = create_random_user(db=db, password=password)

    r = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": user.email, "username": user.username, "password": password},
    )

    assert r.status_code == status.HTTP_409_CONFLICT


# ===========================================
# EMAIL VERIFICATION
# ===========================================


def test_verify_email(client: TestClient, db: Session) -> None:
    user = create_random_user(db=db, email_verified=False)
    db_token = token_service.create_email_verification_token(session=db, db_user=user)
    r = client.get(f"{settings.API_V1_STR}/auth/verify-email?token={db_token.token}")

    assert r.status_code == status.HTTP_200_OK


def test_verify_email_already_verified(client: TestClient, db: Session) -> None:
    user = create_random_user(db=db, email_verified=False)
    db_token = token_service.create_email_verification_token(session=db, db_user=user)

    user_service.update_user(
        session=db,
        db_user=user,
        user_in=UserUpdate(email_verified=True),
    )

    r = client.get(f"{settings.API_V1_STR}/auth/verify-email?token={db_token.token}")

    assert r.status_code == status.HTTP_400_BAD_REQUEST


def test_resend_verificaton_email(mocked_send_email: MagicMock, client: TestClient, db: Session) -> None:
    user = create_random_user(db=db, email_verified=False)

    r = client.post(
        f"{settings.API_V1_STR}/auth/resend-verification",
        json={"email": user.email},
    )

    assert r.status_code == status.HTTP_200_OK


def test_resend_verification_email_already_verified(
    mocked_send_email: MagicMock, client: TestClient, db: Session
) -> None:
    user = create_random_user(db=db)

    r = client.post(
        f"{settings.API_V1_STR}/auth/resend-verification",
        json={"email": user.email},
    )

    assert r.status_code == status.HTTP_400_BAD_REQUEST
