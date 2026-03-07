from os import getenv
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends
# from sqlmodel import Session
from sqlmodel.ext.asyncio.session import AsyncSession
from db.models import *
from db.initialise.initialise import init_async_postgres_db

load_dotenv()

async_engine = init_async_postgres_db(getenv("DB_USER"), getenv("DB_PASSWORD"), getenv("DB_SCHEMA"), getenv("DB_HOST"))

async def get_async_session():
    async with AsyncSession(async_engine) as session:
        yield session

AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]
