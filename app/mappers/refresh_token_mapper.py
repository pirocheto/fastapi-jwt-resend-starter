from app.domain.models.refresh_token import RefreshToken
from app.infrastructure.db.models import RefreshTokenModel


def domain_to_orm(domain_refresh_token: "RefreshToken") -> "RefreshTokenModel":
    """Convert a domain RefreshToken to an ORM RefreshTokenModel."""
    return RefreshTokenModel(
        id=domain_refresh_token.id,
        user_id=domain_refresh_token.user_id,
        hashed_token=domain_refresh_token.hashed_token,
        expires_at=domain_refresh_token.expires_at,
        created_at=domain_refresh_token.created_at,
    )


def orm_to_domain(db_refresh_token: "RefreshTokenModel") -> "RefreshToken":
    """Convert an ORM RefreshTokenModel to a domain RefreshToken."""
    return RefreshToken(
        id=db_refresh_token.id,
        user_id=db_refresh_token.user_id,
        hashed_token=db_refresh_token.hashed_token,
        expires_at=db_refresh_token.expires_at,
        created_at=db_refresh_token.created_at,
    )
