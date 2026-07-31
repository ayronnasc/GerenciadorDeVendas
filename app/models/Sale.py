from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.Item_Sale import Item_Sale
from app.models import Item
from app.models.registry_tables import table_registry


@table_registry.mapped_as_dataclass
class Sale:
    __tablename__ = 'sales'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    description: Mapped[str] = mapped_column(
        server_default='Sale without description'
    )

    total: Mapped[float] = mapped_column(init=False ,server_default='0.00')

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

    items: Mapped[list['Item']] = relationship(
        init=False,
        secondary='item_sale',
        lazy='selectin'
    )
