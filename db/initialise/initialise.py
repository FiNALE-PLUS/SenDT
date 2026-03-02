from pathlib import Path

from sqlalchemy import create_engine, Engine, text
from sqlmodel import SQLModel

import db.models


def init_local_db(path: Path) -> Engine:
    # sqlite_file_name = "database.db"
    sqlite_url = f"sqlite:///{path.with_suffix('.sqlite')}"

    engine = create_engine(sqlite_url)  # , echo=True

    # Enable foreign keys
    with engine.connect() as connection:
        connection.execute(text("PRAGMA foreign_keys = ON;"))

    SQLModel.metadata.create_all(engine)

    return engine

def init_postgres_db(username: str, pw: str, schema: str, host: str = 'localhost:5432') -> Engine:
    url = f'postgresql+psycopg2://{username}:{pw}@{host}/{schema}'

    # print(url)

    engine = create_engine(url)

    # SQLModel.metadata.create_all(engine)

    return engine