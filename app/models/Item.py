from datetime import datetime
from enum import Enum

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship

from app.models.Item_Sale import Item_Sale

table_registry = registry()


class ItemState(str, Enum):
    avaible = 'avaible'
    unavaible = 'unavaible'
    trash = 'trash'


@table_registry.mapped_as_dataclass
class Item:
    __tablename__ = 'items'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    title: Mapped[str]
    description: Mapped[str]
    amount: Mapped[int] = mapped_column(init=False, server_default='0')
    value: Mapped[float] = mapped_column(init=False, server_default='0.00')

    state: Mapped[ItemState] = mapped_column(
        init=False, server_default=ItemState.avaible
    )
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    item_sale: Mapped[list['Item_Sale']] = relationship(
        init=False, cascade='all, delete-orphan', lazy='selectin'
    )
