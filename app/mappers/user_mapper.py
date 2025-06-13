from app.domain.models.user import User
from app.infrastructure.db.models import UserModel


def orm_to_domain(user_model: UserModel) -> User:
    return User(
        id=user_model.id,
        email=user_model.email,
        hashed_password=user_model.hashed_password,
        is_verified=user_model.is_verified,
        created_at=user_model.created_at,
        updated_at=user_model.updated_at,
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
