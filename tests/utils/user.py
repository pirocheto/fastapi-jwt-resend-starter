import faker
from sqlalchemy.orm import Session

from app.models import User
from app.schemas.user import UserCreate
from app.services import token_service, user_service

fake = faker.Faker("fr_FR")


def create_random_user(
    *,
    db: Session,
    email: str | None = None,
    password: str | None = None,
    username: str | None = None,
    email_verified: bool = True,
) -> User:
    email = email or fake.email()
    password = password or fake.password()
    username = username or fake.user_name()

    user_in = UserCreate(
        email=email,
        username=username,
        password=password,
        email_verified=email_verified,
    )
    user = user_service.create_user(session=db, user_create=user_in)
    return user


def user_authentication_headers(*, db_user: User) -> dict[str, str]:
    access_token = token_service.create_access_token(db_user=db_user)
    headers = {"Authorization": f"Bearer {access_token}"}
    return headers
