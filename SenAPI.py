import asyncio

from fastapi import FastAPI, APIRouter

from api.routers import auth_router, chart_router, blob_router
from db.session.models import configure_db_tables
from db.session.records import configure_default_db_enums


async def on_startup():
    configure_db_tables()
    await configure_default_db_enums()


app = FastAPI(on_startup=[on_startup])  # lifespan=lifespan

v1_api_router = APIRouter(prefix="/api/v1")
v1_api_router.include_router(auth_router)
v1_api_router.include_router(chart_router)
v1_api_router.include_router(blob_router)

app.include_router(v1_api_router, tags=["v1"])


@app.get("/")
async def root():
    return {"message": "Hello from SenDT"}