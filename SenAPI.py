import asyncio
from os import getenv

from fastapi import Depends, FastAPI, APIRouter, Response, status
from fastapi_limiter.depends import RateLimiter
from pyrate_limiter import Duration, Limiter, Rate
from sqlalchemy import NullPool
from sqlmodel import SQLModel

from api.routers import admin_router, auth_router, chart_router, blob_router, song_router
from db.initialise.initialise import init_postgres_db
from db.session.records import configure_default_db_enums


# Required to create schema
import db.models

app_endpoint_rate_limit = Depends(RateLimiter(limiter=Limiter(Rate(100, Duration.MINUTE))))

async def on_startup():
    sync_engine = init_postgres_db(getenv("DB_USER"), getenv("DB_PASSWORD"), getenv("DB_SCHEMA"), getenv("DB_HOST"))
    SQLModel.metadata.create_all(bind=sync_engine)
    # sync_engine.pool = NullPool()
    await configure_default_db_enums()

app_summary = r"""
The API to be used by the SenDT front end to manage data for all collaborators.
""".strip()


app = FastAPI(on_startup=[on_startup], title='SenDT API', summary=app_summary, dependencies=[app_endpoint_rate_limit])

v1_api_router = APIRouter(prefix="/api/v1")
v1_api_router.include_router(admin_router)
v1_api_router.include_router(auth_router)
v1_api_router.include_router(chart_router)
v1_api_router.include_router(blob_router)
v1_api_router.include_router(song_router)

app.include_router(v1_api_router, tags=["v1"])


@app.get("/")
async def root():
    return {"message": "Hello from SenDT"}