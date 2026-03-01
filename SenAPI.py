from fastapi import FastAPI, APIRouter

from api.routers import auth_router, chart_router
app = FastAPI()

v1_api_router = APIRouter(prefix="/api/v1")
v1_api_router.include_router(chart_router)
v1_api_router.include_router(auth_router)

app.include_router(v1_api_router, tags=["v1"])


@app.get("/")
async def root():
    return {"message": "Hello from SenDT"}
