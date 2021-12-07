from typing import Any

from fastapi import APIRouter

from models.tag import Tag

router = APIRouter()


@router.get("/", response_model=Any)
async def read_tags():
    """
    Retrieve all items.
    """
    return await Tag.all().values()
