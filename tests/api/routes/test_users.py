from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from tests.utils.user import create_random_user, user_authentication_headers


def test_get_users_me(client: TestClient, db: Session) -> None:
    user = create_random_user(db=db, is_verified=True)
    headers = user_authentication_headers(user_id=user.id)

    r = client.get(f"{settings.API_V1_STR}/users/me", headers=headers)
    current_user = r.json()
    assert r.status_code == 200
    assert current_user["email"] == user.email
