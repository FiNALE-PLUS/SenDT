from fastapi import APIRouter

chart_router = APIRouter(prefix='/chart', tags=['Charts'])


@chart_router.get("/")
async def read_users():
    return [{'chart_data': None}]