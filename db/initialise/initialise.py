from pathlib import Path

from sqlalchemy import create_engine, Engine, text
from sqlmodel import SQLModel


def init_db(path: Path) -> Engine:
    # sqlite_file_name = "database.db"
    sqlite_url = f"sqlite:///{path.with_suffix('.sqlite')}"

    engine = create_engine(sqlite_url)  # , echo=True

    # Enable foreign keys
    with engine.connect() as connection:
        connection.execute(text("PRAGMA foreign_keys = ON;"))

    SQLModel.metadata.create_all(engine)

    return engine