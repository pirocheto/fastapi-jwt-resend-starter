import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions.user_exceptions import UserAlreadyExistsError
from app.infrastructure.db.models import PasswordResetTokenModel, UserModel, VerificationTokenModel
from app.infrastructure.security import hashing, tokens
from app.schemas.user import UserCreate
from tests.utils import fake


class UserFactory:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        email: str | None = None,
        password: str | None = None,
        is_verified: bool = True,
        commit: bool = True,
    ) -> UserModel:
        """
        Create a user with the given parameters.
        If commit is True, the user will be added to the session and committed.
        """
        user_create = UserCreate(
            email=email or fake.email(),
            password=password or fake.password(),
            is_verified=is_verified,
        )

        statement = select(UserModel).where(UserModel.email == user_create.email)
        result = await self.session.execute(statement)
        user = result.scalar_one_or_none()
        if user:
            raise UserAlreadyExistsError()

        update_dict = user_create.model_dump(exclude_unset=True, exclude={"password"})
        update_dict["hashed_password"] = hashing.get_password_hash(user_create.password)

        db_user = UserModel(**update_dict)

        if commit:
            self.session.add(db_user)
            try:
                await self.session.commit()
                await self.session.refresh(db_user)
            except IntegrityError:
                await self.session.rollback()
                raise UserAlreadyExistsError()

        return db_user


class PasswordResetTokenFactory:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self, user_id: uuid.UUID, token: str | None = None, commit: bool = True
    ) -> PasswordResetTokenModel:
        """
        Create a password reset token for the given user.
        If commit is True, the token will be added to the session and committed.
        """
        token = token or tokens.create_opaque_token()
        hashed_token = hashing.get_token_hash(token)

        db_token = PasswordResetTokenModel(
            user_id=user_id,
            hashed_token=hashed_token,
        )

        if commit:
            self.session.add(db_token)
            await self.session.commit()
            await self.session.refresh(db_token)

        return db_token


class VerificationTokenFactory:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self, user_id: uuid.UUID, token: str | None = None, commit: bool = True
    ) -> VerificationTokenModel:
        """
        Create a verification token for the given user.
        If commit is True, the token will be added to the session and committed.
        """
        token = token or tokens.create_opaque_token()
        hashed_token = hashing.get_token_hash(token)

        db_token = VerificationTokenModel(
            user_id=user_id,
            hashed_token=hashed_token,
        )

        if commit:
            self.session.add(db_token)
            await self.session.commit()
            await self.session.refresh(db_token)

        return db_token
