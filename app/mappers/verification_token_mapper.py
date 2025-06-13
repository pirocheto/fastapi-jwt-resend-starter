from app.domain.models.verification_token import VerificationToken
from app.infrastructure.db.models import VerificationTokenModel


def domain_to_orm(domain_refresh_token: VerificationToken) -> VerificationTokenModel:
    """Convert a domain RefreshToken to an ORM RefreshTokenModel."""
    return VerificationTokenModel(
        id=domain_refresh_token.id,
        user_id=domain_refresh_token.user_id,
        hashed_token=domain_refresh_token.hashed_token,
        expires_at=domain_refresh_token.expires_at,
        created_at=domain_refresh_token.created_at,
    )


def orm_to_domain(db_verif_token: VerificationTokenModel) -> VerificationToken:
    """Convert an ORM RefreshTokenModel to a domain RefreshToken."""
    return VerificationToken(
        id=db_verif_token.id,
        user_id=db_verif_token.user_id,
        hashed_token=db_verif_token.hashed_token,
        expires_at=db_verif_token.expires_at,
        created_at=db_verif_token.created_at,
    )
