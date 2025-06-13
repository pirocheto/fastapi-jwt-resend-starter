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


def domain_to_orm(domain_user: User) -> UserModel:
    return UserModel(
        id=domain_user.id,
        email=domain_user.email,
        hashed_password=domain_user.hashed_password,
        is_verified=domain_user.is_verified,
        created_at=domain_user.created_at,
        updated_at=domain_user.updated_at,
    )
