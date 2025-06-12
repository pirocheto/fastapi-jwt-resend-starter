from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.exceptions import (
    EmailNotVerified,
    PasswordIncorrect,
    UserAlreadyExists,
    UserInactive,
    UserNotFound,
)
from app.models import User
from app.schemas.user import UserCreate, UserUpdate


async def create_user(*, async_session: AsyncSession, user_create: UserCreate) -> User:
    statement = select(User).where(User.email == user_create.email)
    result = await async_session.execute(statement)
    user = result.scalar_one_or_none()
    if user:
        raise UserAlreadyExists()

    update_dict = user_create.model_dump(exclude_unset=True, exclude={"password"})
    update_dict["password_hash"] = security.get_password_hash(user_create.password)

    user_obj = User(**update_dict)
    async_session.add(user_obj)

    try:
        await async_session.commit()
        await async_session.refresh(user_obj)
    except IntegrityError:
        await async_session.rollback()
        raise UserAlreadyExists()

    return user_obj


async def delete_user(*, async_session: AsyncSession, db_user: User) -> None:
    await async_session.delete(db_user)
    await async_session.commit()


async def get_user_by_id(*, async_session: AsyncSession, user_id: str) -> User:
    user = await async_session.get(User, user_id)
    if not user:
        raise UserNotFound()
    return user


async def get_user_by_email(*, async_session: AsyncSession, email: str) -> User:
    statement = select(User).where(User.email == email)
    result = await async_session.execute(statement)
    db_user = result.scalar_one_or_none()

    if not db_user:
        raise UserNotFound()

    return db_user


async def update_user(*, async_session: AsyncSession, db_user: User, user_in: UserUpdate) -> User:
    update_dict = user_in.model_dump(exclude_unset=True, exclude={"password"})

    if "email" in update_dict:
        statement = select(User).where(User.email == update_dict["email"])
        result = await async_session.execute(statement)
        user = result.scalar_one_or_none()
        if user:
            raise UserAlreadyExists()

    if user_in.password:
        update_dict["password_hash"] = security.get_password_hash(user_in.password)

    for key, value in update_dict.items():
        setattr(db_user, key, value)

    async_session.add(db_user)
    try:
        await async_session.commit()
        await async_session.refresh(db_user)
    except IntegrityError:
        await async_session.rollback()
        raise UserAlreadyExists()

    return db_user


async def authenticate(*, async_session: AsyncSession, email: str, password: str) -> User:
    db_user = await get_user_by_email(async_session=async_session, email=email)
    if not security.verify_password(password, db_user.password_hash):
        raise PasswordIncorrect()

    if not db_user.is_active:
        raise UserInactive()
    if not db_user.email_verified:
        raise EmailNotVerified()

    return db_user


def validate_password(*, db_user: User, password: str) -> None:
    if not security.verify_password(password, db_user.password_hash):
        raise PasswordIncorrect()
