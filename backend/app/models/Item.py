from datetime import datetime
from enum import Enum

import sqlalchemy as sa
from sqlalchemy import ForeignKey, func, text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models.registry_tables import table_registry


class ItemState(str, Enum):
    available = 'available'
    unavailable = 'unavailable'
    trash = 'trash'


@table_registry.mapped_as_dataclass
class Item:
    __tablename__ = 'items'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    title: Mapped[str]

    description: Mapped[str]

    amount: Mapped[int] = mapped_column(server_default='0')
    value: Mapped[float] = mapped_column(server_default='0.00')

    state: Mapped[ItemState] = mapped_column(
        sa.Enum(ItemState, name='itemstate'),
        server_default=text("'available'::itemstate"),
    )
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
