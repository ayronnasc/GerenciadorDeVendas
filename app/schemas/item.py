from datetime import datetime

from pydantic import BaseModel, Field

from app.models.Item import ItemState


class ItemSchema(BaseModel):
    title: str
    description: str
    value: float
    amount: int
    state: ItemState = Field(default=ItemState.available)

    model_config = {"from_attributes": True}

#Parei aqui! preciso criar outro itempublic para o view do proprio item!
class ItemPublic(BaseModel):
    id: int
    title: str
    description: str
    state: ItemState = Field(default=ItemState.available)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ItemList(BaseModel):
    items: list[ItemPublic]


class ItemUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    value: float | None = None
    amount: int | None = None
    state: ItemState | None = None
