import secrets
import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core import security
from app.core.exceptions import UserAlreadyExists
from app.models import EmailVerificationToken, PasswordResetToken, RefreshToken, User
from app.schemas.user import UserCreate
from tests.utils import fake


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
        commit: bool = True,
    ) -> User:
        user_create = UserCreate(
            email=email or fake.email(),
            username=username or fake.user_name(),
            password=password or fake.password(),
            email_verified=email_verified,
            is_superuser=is_superuser,
            is_active=is_active,
        )

        statement = select(User).where(User.email == user_create.email)
        user = self.session.execute(statement).scalar_one_or_none()
        if user:
            raise UserAlreadyExists()

        update_dict = user_create.model_dump(exclude_unset=True, exclude={"password"})
        update_dict["password_hash"] = security.get_password_hash(user_create.password)

        user_obj = User(**update_dict)

        if commit:
            self.session.add(user_obj)
            try:
                self.session.commit()
                self.session.refresh(user_obj)
            except IntegrityError:
                self.session.rollback()
                raise UserAlreadyExists()

        return user_obj


class PasswordResetTokenFactory:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self, user_id: uuid.UUID, token: str | None = None, used: bool = False, commit: bool = True
    ) -> PasswordResetToken:
        token_obj = PasswordResetToken(
            user_id=user_id,
            token=token or secrets.token_urlsafe(64),
            expires_at=fake.future_datetime(end_date="+1d"),
            used=used,
        )
        if commit:
            self.session.add(token_obj)
            self.session.commit()
            self.session.refresh(token_obj)

        return token_obj


class EmailVerificationTokenFactory:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self, user_id: uuid.UUID, token: str | None = None, used: bool = False, commit: bool = True
    ) -> EmailVerificationToken:
        token_obj = EmailVerificationToken(
            user_id=user_id,
            token=token or secrets.token_urlsafe(64),
            expires_at=fake.future_datetime(end_date="+1d"),
            used=used,
        )
        if commit:
            self.session.add(token_obj)
            self.session.commit()
            self.session.refresh(token_obj)

        return token_obj


class RefreshTokenFactory:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self, user_id: uuid.UUID, token: str | None = None, is_revoked: bool = False, commit: bool = True
    ) -> RefreshToken:
        token_obj = RefreshToken(
            user_id=user_id,
            token=token or secrets.token_urlsafe(64),
            expires_at=fake.future_datetime(end_date="+1d"),
            is_revoked=is_revoked,
        )
        if commit:
            self.session.add(token_obj)
            self.session.commit()
            self.session.refresh(token_obj)

        return token_obj
