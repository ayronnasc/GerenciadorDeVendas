from datetime import datetime

from pydantic import BaseModel

from app.schemas.item_sale import ItemSalePublic, ItemSaleSchema


class SaleSchema(BaseModel):
    description: str
    items: list[ItemSaleSchema]


class SalePublic(SaleSchema):
    id: int
    items: list[ItemSalePublic]
    created_at: datetime
    updated_at: datetime


class SaleList(BaseModel):
    todos: list[SalePublic]


class SaleUpdate(BaseModel):
    description: str | None = None
    items: list[ItemSaleSchema] | None = None
