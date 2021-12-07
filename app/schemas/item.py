from typing import List, Optional
from uuid import UUID

from pydantic import AnyHttpUrl, Field, validator
from pydantic.main import BaseModel
from tortoise import Tortoise
from tortoise.contrib.pydantic import pydantic_model_creator

from models.item import Item

Tortoise.init_models(["models.item"], "models")
ItemOut = pydantic_model_creator(Item, exclude=['next', 'previous'])


class ItemCreate(BaseModel):
    next_id: Optional[int] = None
    previous_id: Optional[int] = None
    url: AnyHttpUrl
    thumbnail: Optional[AnyHttpUrl]
    tags: Optional[List[str]]

    price: float
    is_favorite: bool = Field(default=False)
    quantity: int = Field(default=1)

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "url"      : "https://www.some.domain.com/product/1",
                "thumbnail": "https://www.some.domain.com/product/1/assets/favicon.ico",
                "price"    : 35.4,
                "tags"     : ['cheap'],
            }
        }

    # @validator('*',pre=True)
    # def validate(cls, v):
    #     if "previous_id" in v.keys() and "next_id" in v.keys():
    #         raise ValueError(f"Only one should be set {v}")
    #     return v


class ItemPatch(BaseModel):
    next_id: Optional[int]
    previous_id: Optional[int]
    url: Optional[AnyHttpUrl]
    thumbnail: Optional[AnyHttpUrl]
    tags: Optional[List[str]]

    price: Optional[float]
    is_favorite: Optional[bool]
    quantity: Optional[int]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "url"      : "https://www.some.domain.com/product/1",
                "thumbnail": "https://www.some.domain.com/product/1/assets/favicon.ico",
                "price"    : 35.4,
                "tags"     : ['cheap'],
            }
        }


class ItemDelete(BaseModel):
    id: int


class ItemOutWithTagsSerialized(ItemOut):
    tags: List[str]