from os import getenv
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends
from sqlmodel import Session
from db.models import *
from db.initialise.initialise import init_postgres_db

load_dotenv()

engine = init_postgres_db(getenv("DB_USER"), getenv("DB_PASSWORD"), getenv("DB_SCHEMA"), getenv("DB_HOST"))

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]