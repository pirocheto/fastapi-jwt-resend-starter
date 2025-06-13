from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions.user_exceptions import UserAlreadyExistsError
from app.infrastructure.db.models import UserModel
from app.infrastructure.security import hashing
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
        If commit is True, the user will be added to the async_session and committed.
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

        user_obj = UserModel(**update_dict)

        if commit:
            self.session.add(user_obj)
            try:
                await self.session.commit()
                await self.session.refresh(user_obj)
            except IntegrityError:
                await self.session.rollback()
                raise UserAlreadyExistsError()

        return user_obj
