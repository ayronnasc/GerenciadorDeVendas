from pydantic import BaseModel


class ItemSaleSchema(BaseModel):
    sale_id: int
    item_id: int
    user_id: int
    amount: int
    value: int


class ItemSalePublic(ItemSaleSchema):
    id: int
