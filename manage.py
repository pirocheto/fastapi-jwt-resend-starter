import logging

import typer

app = typer.Typer()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.command()
def init_database() -> None:
    """
    Initialize the database.
    """
    from sqlalchemy.orm import Session

    from app.core.database import engine, init_db

    def init() -> None:
        with Session(engine) as session:
            init_db(session)

    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")


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
