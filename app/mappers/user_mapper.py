from app.domain.models.user import User
from app.infrastructure.db.models import UserModel


def orm_to_domain(db_model: UserModel) -> User:
    return User(
        id=db_model.id,
        email=db_model.email,
        hashed_password=db_model.hashed_password,
        is_verified=db_model.is_verified,
        created_at=db_model.created_at,
        updated_at=db_model.updated_at,
    )


def domain_to_orm(user: User) -> UserModel:
    return UserModel(
        id=user.id,
        email=user.email,
        hashed_password=user.hashed_password,
        is_verified=user.is_verified,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )
