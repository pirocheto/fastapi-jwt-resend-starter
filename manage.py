import logging

import typer

app = typer.Typer()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.command()
def init_database() -> None:
    """
    Initialize the database with initial data.
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
def run_tests() -> None:
    """
    Run the test suite.
    """
    import subprocess

    subprocess.run(["bash", "scripts/test.sh"], check=False)


@app.command()
def build_emails() -> None:
    """
    Build email templates.
    """
    import subprocess

    subprocess.run(["bash", "scripts/build-emails.sh"], check=False)


if __name__ == "__main__":
    app()
