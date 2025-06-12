from app.domain.models.user import User
from app.infrastructure.db.models.user_model import UserModel


def orm_to_domain(user_model: UserModel) -> User:
    return User(
        id=user_model.id,
        email=user_model.email,
        hashed_password=user_model.hashed_password,
        is_verified=user_model.is_verified,
        is_active=user_model.is_active,
        created_at=user_model.created_at,
        updated_at=user_model.updated_at,
    )


def domain_to_orm(user: User) -> UserModel:
    user_model = UserModel()
    user_model.id = user.id
    user_model.email = user.email
    user_model.hashed_password = user.hashed_password
    user_model.is_verified = user.is_verified
    user_model.is_active = user.is_active
    return user_model
