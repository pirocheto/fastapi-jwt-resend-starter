from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from tests.utils.user import create_random_user, user_authentication_headers


def test_get_users_me(client: TestClient, db: Session) -> None:
    user = create_random_user(db=db, email_verified=True)
    headers = user_authentication_headers(db_user=user)

    r = client.get(f"{settings.API_V1_STR}/users/me", headers=headers)
    assert r.status_code == status.HTTP_200_OK
