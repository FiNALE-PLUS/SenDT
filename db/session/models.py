from sqlmodel import SQLModel

from .session import engine


def configure_db_tables():
    SQLModel.metadata.create_all(bind=engine)