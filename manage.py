import logging

import typer

app = typer.Typer()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.command()
def init() -> None:
    """
    Initialize the database.
    """

    import asyncio

    from app.infrastructure.db.utils import init_db

    asyncio.run(init_db())


if __name__ == "__main__":
    app()
