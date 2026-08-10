from typing import Optional

from pydantic import BaseModel

from backend.app.schemas.item import ItemPublic


class ItemSaleSchema(BaseModel):
    sale_id: int
    item_id: int
    amount: int
    value: float

    model_config = {'from_attributes': True}


class ItemSaleCreate(BaseModel):
    item_id: int
    amount: int


class ItemSalePublic(BaseModel):
    amount: int
    value: float

    item: ItemPublic

    model_config = {'from_attributes': True}


class ItemSaleUpdate(BaseModel):
    item_id: int
    amount: Optional[int] = None

    delete: Optional[bool] = False
