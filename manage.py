import logging

import typer

from app.core.config import settings

app = typer.Typer()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.command()
def createsuperuser(
    email: str = typer.Option(settings.DEFAULT_SUPERUSER_EMAIL, "--email", "-e", help="Email for the superuser"),
    username: str = typer.Option(
        settings.DEFAULT_SUPERUSER_USERNAME, "--username", "-u", help="Username for the superuser"
    ),
    password: str = typer.Option(
        settings.DEFAULT_SUPERUSER_PASSWORD, "--password", "-p", help="Password for the superuser"
    ),
) -> None:
    """
    Create a superuser with the given email, username, and password.
    """
    from sqlalchemy.orm import Session

    from app.core.database import engine, init_superuser

    with Session(engine) as async_session:
        init_superuser(
            async_session=async_session,
            email=email,
            username=username,
            password=password,
        )


@app.command()
def init() -> None:
    """
    Initialize the database.
    """
    from sqlalchemy.orm import Session

    from app.core.database import engine, init_db

    with Session(engine) as async_session:
        init_db(async_session)


if __name__ == "__main__":
    app()
