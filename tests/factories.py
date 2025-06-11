from faker import Faker  # type: ignore[import-untyped]
from sqlalchemy.orm import Session

from app.models import User
from app.schemas.user import UserCreate
from app.services import user_service

fake = Faker("fr_FR")


class UserFactory:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        email: str | None = None,
        username: str | None = None,
        password: str | None = None,
        email_verified: bool = True,
        is_superuser: bool = False,
        is_active: bool = True,
    ) -> User:
        user_create = UserCreate(
            email=email or fake.email(),
            username=username or fake.user_name(),
            password=password or fake.password(),
            email_verified=email_verified,
            is_superuser=is_superuser,
            is_active=is_active,
        )

        return user_service.create_user(
            session=self.session,
            user_create=user_create,
        )
