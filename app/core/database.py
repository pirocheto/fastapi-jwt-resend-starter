from collections.abc import Generator
from logging import getLogger
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import User
from app.schemas.user import UserCreate
from app.services import user_service

logger = getLogger(__name__)


engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def init_superuser(session: Session) -> None:
    statement = select(User).where(User.email == settings.FIRST_SUPERUSER)
    user = session.execute(statement).scalar_one_or_none()

    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            username=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
            email_verified=True,
        )
        user = user_service.create_user(session=session, user_create=user_in)
        logger.info(f"Created superuser {user.email}")
    else:
        logger.info(f"Superuser {user.email} already exists")


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    from app.models import Base

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
