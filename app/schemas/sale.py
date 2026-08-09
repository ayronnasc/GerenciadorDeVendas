from datetime import datetime

from pydantic import BaseModel, Field

from typing import List, Optional

from app.schemas.item_sale import (
    ItemSaleSchema,
    ItemSaleCreate,
    ItemSalePublic,
    ItemSaleUpdate
)

from app.schemas.item import ItemPublic


class SaleSchema(BaseModel):
    description: str
    items: list[ItemSaleCreate]

    model_config = {"from_attributes": True}    

class SaleItemPublic(BaseModel):
    amount: int 
    value: float
    items: ItemPublic


class SalePublic(SaleSchema):
    id: int
    total: float
    items: list[ItemSalePublic] = Field(validation_alias="item_sale")
    created_at: datetime
    updated_at: datetime


class SaleList(BaseModel):
    sales: list[SalePublic]


class SaleUpdate(BaseModel):
    description: str | None = None
    items: list[ItemSaleUpdate] | None = None

class SaleResponse(BaseModel):
    sale: Optional[SalePublic] = None
    message: Optional[str] = None
