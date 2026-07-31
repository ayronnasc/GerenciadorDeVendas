from datetime import datetime

from pydantic import BaseModel, Field

from app.models.Item import ItemState


class ItemSchema(BaseModel):
    title: str
    description: str
    value: float
    amount: int
    state: ItemState = Field(default=ItemState.avaible)


class ItemPublic(ItemSchema):
    id: int
    created_at: datetime
    updated_at: datetime


class ItemList(BaseModel):
    todos: list[ItemPublic]


class ItemUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    value: float | None = None
    amount: int | None = None
    state: ItemState | None = None
