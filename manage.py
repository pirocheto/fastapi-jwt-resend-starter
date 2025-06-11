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

    with Session(engine) as session:
        init_superuser(
            session=session,
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

    with Session(engine) as session:
        init_db(session)


@app.command()
def test(
    marker: str = typer.Option(
        None, "--marker", "-m", help="Pytest marker to select tests (default: all markers tested)"
    ),
) -> None:
    """
    Run the test suite with an optional marker.
    """
    import sys

    import coverage
    import pytest

    cov = coverage.Coverage(source=["app"])
    cov.start()

    pytest_args = []
    if marker:
        pytest_args += ["-m", marker]

    exit_code = pytest.main(pytest_args)

    cov.stop()
    cov.save()

    cov.report(show_missing=True)
    cov.html_report(title="coverage")

    if exit_code != 0:
        sys.exit(exit_code)


if __name__ == "__main__":
    app()
