from fastapi import APIRouter

# from app.api.api_v1.endpoints import items, login, users, utils
from api.api_v1.endpoints import items, tags

api_router = APIRouter()
api_router.include_router(tags.router, prefix="/tags", tags=["tags"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
