from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import security
from app.models import User
from app.schemas.user import UserCreate, UserUpdate


def create_user(*, session: Session, user_create: "UserCreate") -> User:
    """
    Create a new user in the database.
    """
    update_dict = user_create.model_dump(exclude_unset=True, exclude={"password"})
    update_dict["password_hash"] = security.get_password_hash(user_create.password)

    db_obj = User(**update_dict)

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def delete_user(*, session: Session, db_user: User) -> None:
    """
    Delete a user from the database.
    """
    session.delete(db_user)
    session.commit()


def get_user_by_id(*, session: Session, user_id: str) -> User | None:
    """
    Get a user by ID from the database.
    """
    return session.get(User, user_id)


def get_user_by_email(*, session: Session, email: str) -> User | None:
    """
    Get a user by email from the database.
    """
    statement = select(User).where(User.email == email)
    session_user = session.execute(statement).scalar_one_or_none()
    return session_user


def update_user(*, session: Session, db_user: User, user_in: "UserUpdate") -> User:
    """
    Update a user in the database.
    """
    update_dict = user_in.model_dump(exclude_unset=True, exclude={"password"})
    if user_in.password:
        update_dict["password_hash"] = security.get_password_hash(user_in.password)

    for key, value in update_dict.items():
        setattr(db_user, key, value)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def verify_user_email(*, session: Session, db_user: User) -> User | None:
    """
    Verify a user's email address in the database.
    """
    db_user.email_verified = True
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    """
    Authenticate a user by email and password.
    """
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not security.verify_password(password, db_user.password_hash):
        return None
    return db_user
