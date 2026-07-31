from datetime import datetime

from pydantic import BaseModel, Field

from app.models.Item import ItemState


class ItemSchema(BaseModel):
    title: str
    description: str
    value: float
    amount: int
    state: ItemState = Field(default=ItemState.available)


class ItemPublic(ItemSchema):
    id: int
    created_at: datetime
    updated_at: datetime


class ItemList(BaseModel):
    items: list[ItemPublic]


class ItemUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    value: float | None = None
    amount: int | None = None
    state: ItemState | None = None
