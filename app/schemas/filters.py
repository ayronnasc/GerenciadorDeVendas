from pydantic import BaseModel, Field

from app.models.Item import ItemState


class FilterPage(BaseModel):
    offset: int = Field(ge=0, default=0)
    limit: int = Field(ge=0, default=10)


class FilterItem(FilterPage):
    title: str | None = Field(default=None, min_length=3, max_length=20)
    description: str | None = None
    state: ItemState | None = None
    value: float | None = None
    amount: int | None = None


class FilterSale(FilterPage):
    description: str | None = Field(default=None)
    total: float | None = None
