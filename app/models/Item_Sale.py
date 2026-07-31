from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.registry_tables import table_registry


@table_registry.mapped_as_dataclass
class Item_Sale:
    __tablename__ = 'item_sale'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)

    amount: Mapped[int] = mapped_column(server_default='0')
    value: Mapped[float] = mapped_column(server_default='0.00')

    item_id: Mapped[int] = mapped_column(ForeignKey('items.id'))
    sale_id: Mapped[int] = mapped_column(ForeignKey('sales.id'))

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
