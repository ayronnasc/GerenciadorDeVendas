from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, registry

table_registry = registry()


@table_registry.mapped_as_dataclass
class Item_Sale:
    __tablename__ = 'Item_Sale'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)

    amount: Mapped[int] = mapped_column(init=False, server_default='0')
    value: Mapped[float] = mapped_column(init=False, server_default='0.00')

    item_id: Mapped[int] = mapped_column(ForeignKey('items.id'))
    sale_id: Mapped[int] = mapped_column(ForeignKey('sales.id'))

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
