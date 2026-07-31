from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.Item import Item
from app.models.Item_Sale import Item_Sale
from app.models.Sale import Sale

from app.models.registry_tables import table_registry

@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )

    items: Mapped[list['Item']] = relationship(
        init=False, cascade='all, delete-orphan', lazy='selectin'
    )

    sales: Mapped[list['Sale']] = relationship(
        init=False, cascade='all, delete-orphan', lazy='selectin'
    )

    item_sale: Mapped[list['Item_Sale']] = relationship(
        init=False, cascade='all, delete-orphan', lazy='selectin'
    )
