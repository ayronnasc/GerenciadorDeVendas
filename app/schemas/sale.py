from datetime import datetime

from pydantic import BaseModel

from typing import List

from app.schemas.item_sale import (
    ItemSaleSchema,
    ItemSaleCreate
)

from app.schemas.item import ItemPublic


class SaleSchema(BaseModel):
    description: str
    items: list[ItemSaleCreate]
    

class SaleItemPublic(BaseModel):
    amount: int 
    value: float
    items: ItemPublic


class SalePublic(SaleSchema):
    id: int
    total: float
    items: list[ItemPublic]
    created_at: datetime
    updated_at: datetime


class SaleList(BaseModel):
    todos: list[SalePublic]


class SaleUpdate(BaseModel):
    description: str | None = None
    items: list[ItemSaleSchema] | None = None
