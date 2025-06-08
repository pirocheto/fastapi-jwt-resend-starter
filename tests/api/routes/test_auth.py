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


# ===========================================
# AUTHENTICATION: LOGIN
# ===========================================


def test_login_user(client: TestClient, db: Session) -> None:
    """
    GIVEN a registered user with valid credentials
    WHEN the user logs in
    THEN they receive valid access and refresh tokens
    """
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
    """
    GIVEN invalid login credentials
    WHEN a login attempt is made
    THEN the system responds with 401
    """
    email = fake.email()
    password = fake.password()
    r = client.post(
        f"{settings.API_V1_STR}/auth/token",
        data={"username": email, "password": password},
    )

    assert r.status_code == status.HTTP_401_UNAUTHORIZED
    assert r.json() == {"detail": messages.ERROR_INVALID_CREDENTIALS}


def test_login_user_not_verified(client: TestClient, db: Session) -> None:
    """
    GIVEN a user who has not verified their email
    WHEN they attempt to log in
    THEN the system denies access with 401
    """
    password = fake.password()
    user = create_random_user(db=db, password=password, is_verified=False)

    r = client.post(
        f"{settings.API_V1_STR}/auth/token",
        data={"username": user.email, "password": password},
    )

    assert r.status_code == status.HTTP_401_UNAUTHORIZED
    assert r.json() == {"detail": messages.ERROR_EMAIL_NOT_VERIFIED}


# ===========================================
# AUTHENTICATION: REFRESH TOKEN
# ===========================================


def test_refresh_access_token(client: TestClient, db: Session) -> None:
    """
    GIVEN a valid refresh token
    WHEN the token is submitted for renewal
    THEN a new access token is returned
    """
    password = fake.password()
    user = create_random_user(db=db, password=password)

    login_response = client.post(
        f"{settings.API_V1_STR}/auth/token",
        data={"username": user.email, "password": password},
    )
    refresh_token = login_response.json()["refresh_token"]

    r = client.post(
        f"{settings.API_V1_STR}/auth/token/refresh",
        json={"refresh_token": refresh_token},
    )

    assert r.status_code == status.HTTP_200_OK
    assert "access_token" in r.json()


def test_refresh_access_token_invalid(client: TestClient) -> None:
    """
    GIVEN an invalid refresh token
    WHEN the token is submitted
    THEN the system returns a 401 error
    """
    r = client.post(
        f"{settings.API_V1_STR}/auth/token/refresh",
        json={"refresh_token": "invalid_token"},
    )

    assert r.status_code == status.HTTP_401_UNAUTHORIZED
    assert r.json() == {"detail": messages.ERROR_INVALID_CREDENTIALS}


def test_refresh_access_token_user_not_found(client: TestClient, db: Session) -> None:
    """
    GIVEN a refresh token from a deleted user
    WHEN the token is submitted
    THEN the system returns a 404
    """
    password = fake.password()
    user = create_random_user(db=db, password=password)

    login_response = client.post(
        f"{settings.API_V1_STR}/auth/token",
        data={"username": user.email, "password": password},
    )
    refresh_token = login_response.json()["refresh_token"]

    user_service.delete_user(session=db, db_user=user)

    r = client.post(
        f"{settings.API_V1_STR}/auth/token/refresh",
        json={"refresh_token": refresh_token},
    )

    assert r.status_code == status.HTTP_404_NOT_FOUND
    assert r.json() == {"detail": messages.ERROR_USER_NOT_FOUND}


# ===========================================
# PASSWORD RESET
# ===========================================


def test_send_email_reset_password(mocked_send_email: MagicMock, client: TestClient, db: Session) -> None:
    """
    GIVEN a valid email
    WHEN requesting password reset
    THEN a reset email is sent
    """
    user = create_random_user(db=db)

    r = client.post(
        f"{settings.API_V1_STR}/auth/password/forgot",
        json={"email": user.email},
    )

    assert r.status_code == status.HTTP_200_OK
    assert mocked_send_email.called
    assert r.json() == {"message": messages.SUCCESS_PASSWORD_RESET_LINK_SENT}


def test_update_password_with_token(client: TestClient, db: Session) -> None:
    """
    GIVEN a valid password reset token
    WHEN a new password is submitted
    THEN the password is updated and the user can log in
    """
    user = create_random_user(db=db)
    token = security.create_password_reset_token(subject=user.id)
    new_password = fake.password()

    r = client.post(
        f"{settings.API_V1_STR}/auth/password/reset",
        json={"token": token, "new_password": new_password},
    )

    assert r.status_code == status.HTTP_200_OK
    assert r.json() == {"message": messages.SUCCESS_PASSWORD_RESET}

    login = client.post(
        f"{settings.API_V1_STR}/auth/token",
        data={"username": user.email, "password": new_password},
    )
    assert login.status_code == status.HTTP_200_OK


def test_update_password(client: TestClient, db: Session) -> None:
    """
    GIVEN an authenticated user
    WHEN they update their password
    THEN the password is changed and can be used to log in
    """
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

    login = client.post(
        f"{settings.API_V1_STR}/auth/token",
        data={"username": user.email, "password": new_password},
    )
    assert login.status_code == status.HTTP_200_OK


# ===========================================
# USER REGISTRATION
# ===========================================


def test_register_new_user(mocked_send_email: MagicMock, client: TestClient) -> None:
    """
    GIVEN a new user registration
    WHEN valid data is submitted
    THEN the user is created and verification email is sent
    """
    email = settings.EMAILS_TEST_RECIPIENT
    username = fake.user_name()
    password = fake.password()

    r = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": email, "username": username, "password": password},
    )

    assert r.status_code == status.HTTP_201_CREATED
    assert r.json() == {"message": messages.SUCCESS_USER_REGISTERED}
    assert mocked_send_email.called


def test_register_existing_user(client: TestClient) -> None:
    """
    GIVEN an existing user
    WHEN they attempt to register again
    THEN the system returns a 409 conflict
    """
    email = settings.EMAILS_TEST_RECIPIENT
    username = fake.user_name()
    password = fake.password()

    r = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": email, "username": username, "password": password},
    )

    assert r.status_code == status.HTTP_409_CONFLICT
    assert r.json() == {"detail": messages.ERROR_USER_ALREADY_EXISTS}


# ===========================================
# EMAIL VERIFICATION
# ===========================================


def test_verify_email(client: TestClient, db: Session) -> None:
    """
    GIVEN a valid verification token
    WHEN accessing the verification link
    THEN the user's email is verified
    """
    user = create_random_user(db=db, is_verified=False)
    token = security.create_email_verification_token(subject=user.id)

    r = client.get(f"{settings.API_V1_STR}/auth/verify-email?token={token}")

    assert r.status_code == status.HTTP_200_OK


def test_verify_email_already_verified(client: TestClient, db: Session) -> None:
    """
    GIVEN a user already verified
    WHEN they re-use a verification token
    THEN the system returns an error
    """
    user_in = UserCreate(
        email=fake.email(),
        username=fake.user_name(),
        password=fake.password(),
        email_verified=True,
    )
    user = user_service.create_user(session=db, user_create=user_in)
    token = security.create_email_verification_token(subject=user.id)

    r = client.get(f"{settings.API_V1_STR}/auth/verify-email?token={token}")

    assert r.status_code == status.HTTP_400_BAD_REQUEST
    assert r.json() == {"detail": messages.ERROR_EMAIL_ALREADY_VERIFIED}


def test_resend_verificaton_email(mocked_send_email: MagicMock, client: TestClient, db: Session) -> None:
    """
    GIVEN a user not yet verified
    WHEN they request a new verification email
    THEN the system sends the email
    """
    user = create_random_user(db=db, is_verified=False)

    r = client.post(
        f"{settings.API_V1_STR}/auth/resend-verification",
        json={"email": user.email},
    )

    assert r.status_code == status.HTTP_200_OK
    assert r.json() == {"message": messages.SUCCESS_EMAIL_VERIFICATION_LINK_SENT}
    assert mocked_send_email.called


def test_resend_verification_email_already_verified(mocked_send_email: MagicMock, client: TestClient, db: Session) -> None:
    """
    GIVEN a verified user
    WHEN they try to request another verification email
    THEN the system returns an error
    """
    user = create_random_user(db=db)

    r = client.post(
        f"{settings.API_V1_STR}/auth/resend-verification",
        json={"email": user.email},
    )

    assert r.status_code == status.HTTP_400_BAD_REQUEST
    assert r.json() == {"detail": messages.ERROR_EMAIL_ALREADY_VERIFIED}
    assert not mocked_send_email.called
