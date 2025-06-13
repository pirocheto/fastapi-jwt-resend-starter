import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions.user_exceptions import UserAlreadyExistsError, UserNotFoundError
from app.domain.models import User, VerificationToken
from app.infrastructure.dao import UserDAO, VerificationTokenDAO
from app.infrastructure.db.models import UserModel, VerificationTokenModel
from app.infrastructure.db.utils import transactional
from app.infrastructure.email import mailer
from app.infrastructure.security import hashing, tokens
from app.schemas.user import UserRegister
from app.utils import mapper


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_dao = UserDAO(session)
        self.verif_token_dao = VerificationTokenDAO(session)

    @transactional
    async def register_user(self, user_in: UserRegister) -> User:
        """Register a new user."""

        existing_user = await self.user_dao.get_by_email(user_in.email)

        if existing_user:
            raise UserAlreadyExistsError()

        # Prepare the user data for saving, excluding the password field
        user_dict = user_in.model_dump(exclude_unset=True, exclude={"password"})
        user_dict["hashed_password"] = hashing.get_hash(user_in.password)

        domain_user = User.model_validate(user_dict)
        db_user = mapper.domain_to_orm(domain_user, UserModel)

        # Create a verification token for the new user
        opaque_token = tokens.create_opaque_token()
        hashed_opaque_token = hashing.get_hash(opaque_token)

        domain_verif_token = VerificationToken(user_id=db_user.id, hashed_token=hashed_opaque_token)
        db_verif_token = mapper.domain_to_orm(domain_verif_token, VerificationTokenModel)

        await self.user_dao.add(db_user)
        await self.verif_token_dao.add(db_verif_token)

        # Send verification email
        email_data = mailer.generate_verification_email(
            email_to=db_user.email,
            token=opaque_token,
        )
        mailer.send_email(
            email_to=db_user.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
            raw_content=email_data.raw_content,
        )
        return domain_user

    async def get_user_by_id(self, id: uuid.UUID) -> User:
        """Retrieve a user by ID."""

        db_user = await self.user_dao.get_by_id(id)

        if not db_user:
            raise UserNotFoundError()

        return mapper.orm_to_domain(db_user, User)
