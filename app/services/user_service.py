from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

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


def create_user(*, session: Session, user_create: UserCreate) -> User:
    """
    Create a new user in the database.
    """
    statement = select(User).where(User.email == user_create.email)
    user = session.execute(statement).scalar_one_or_none()
    if user:
        raise UserAlreadyExists()

    update_dict = user_create.model_dump(exclude_unset=True, exclude={"password"})
    update_dict["password_hash"] = security.get_password_hash(user_create.password)

    user_obj = User(**update_dict)
    session.add(user_obj)

    try:
        session.commit()
        session.refresh(user_obj)
    except IntegrityError:
        session.rollback()
        raise UserAlreadyExists()

    return user_obj


def delete_user(*, session: Session, db_user: User) -> None:
    """
    Delete a user from the database.
    """
    session.delete(db_user)
    session.commit()


def get_user_by_id(*, session: Session, user_id: str) -> User:
    """
    Get a user by ID from the database.
    """
    user = session.get(User, user_id)
    if not user:
        raise UserNotFound()
    return user


def get_user_by_email(*, session: Session, email: str) -> User:
    """
    Get a user by email from the database.
    """
    statement = select(User).where(User.email == email)
    db_user = session.execute(statement).scalar_one_or_none()

    if not db_user:
        raise UserNotFound()

    return db_user


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> User:
    """
    Update a user in the database.
    """
    update_dict = user_in.model_dump(exclude_unset=True, exclude={"password"})

    if "email" in update_dict:
        statement = select(User).where(User.email == update_dict["email"])
        user = session.execute(statement).scalar_one_or_none()
        if user:
            raise UserAlreadyExists()

    if user_in.password:
        update_dict["password_hash"] = security.get_password_hash(user_in.password)

    for key, value in update_dict.items():
        setattr(db_user, key, value)

    session.add(db_user)
    try:
        session.commit()
        session.refresh(db_user)
    except IntegrityError:
        session.rollback()
        raise UserAlreadyExists()

    return db_user


def authenticate(*, session: Session, email: str, password: str) -> User:
    """
    Authenticate a user by email and password.
    """
    db_user = get_user_by_email(session=session, email=email)
    if not security.verify_password(password, db_user.password_hash):
        raise PasswordIncorrect()

    if not db_user.is_active:
        raise UserInactive()
    if not db_user.email_verified:
        raise EmailNotVerified()

    return db_user


def validate_password(*, db_user: User, password: str) -> None:
    """
    Validate a user's password.
    """
    if not security.verify_password(password, db_user.password_hash):
        raise PasswordIncorrect()
