from fastapi import APIRouter

chart_router = APIRouter(prefix='/chart')


@chart_router.get("/")
async def read_users():
    return [{'chart_data': None}]