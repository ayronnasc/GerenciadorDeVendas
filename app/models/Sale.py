from datetime import datetime
from typing import List

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.models.registry_tables import table_registry
from app.models import Item_Sale
from app.models import Item

@table_registry.mapped_as_dataclass
class Sale:
    __tablename__ = 'sales'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)

    total: Mapped[float] = mapped_column(server_default='0.00')

    description: Mapped[str] = mapped_column(
        server_default='Sale without description'
    )

    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    items: Mapped[List["Item_Sale"]] = relationship(
        argument="Item_Sale",
        init=False, 
        cascade='all, '
        'delete-orphan', 
        lazy='selectin'
    )
