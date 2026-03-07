from os import getenv

from sqlalchemy import NullPool
from sqlmodel import SQLModel

from db.initialise.initialise import init_postgres_db

from .session import async_engine

sync_engine = init_postgres_db(getenv("DB_USER"), getenv("DB_PASSWORD"), getenv("DB_SCHEMA"), getenv("DB_HOST"))

def configure_db_tables():
    SQLModel.metadata.create_all(bind=sync_engine)
    sync_engine.pool = NullPool()
    yield True
    return ValueError('DB should only be initialised once.')