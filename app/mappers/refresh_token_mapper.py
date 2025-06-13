from app.domain.models.refresh_token import RefreshToken
from app.infrastructure.db.models import RefreshTokenModel


def domain_to_orm(refresh_token: "RefreshToken") -> "RefreshTokenModel":
    """Convert a domain RefreshToken to an ORM RefreshTokenModel."""
    return RefreshTokenModel(
        id=refresh_token.id,
        user_id=refresh_token.user_id,
        hashed_token=refresh_token.hashed_token,
        expires_at=refresh_token.expires_at,
        created_at=refresh_token.created_at,
    )


def orm_to_domain(refresh_token_domain: "RefreshTokenModel") -> "RefreshToken":
    """Convert an ORM RefreshTokenModel to a domain RefreshToken."""
    return RefreshToken(
        id=refresh_token_domain.id,
        user_id=refresh_token_domain.user_id,
        hashed_token=refresh_token_domain.hashed_token,
        expires_at=refresh_token_domain.expires_at,
        created_at=refresh_token_domain.created_at,
    )
