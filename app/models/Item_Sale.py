from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models import Item, Sale

from typing import Optional

from app.models.registry_tables import table_registry


@table_registry.mapped_as_dataclass
class Item_Sale:#association_table
    __tablename__ = 'item_sale'

    item_id: Mapped[int] = mapped_column(ForeignKey('items.id'), primary_key=True, init=False)
    sale_id: Mapped[int] = mapped_column(ForeignKey('sales.id'), primary_key=True, init=False)

    amount: Mapped[Optional[int]]
    value: Mapped[Optional[float]]

    items: Mapped["Item"] = relationship()
