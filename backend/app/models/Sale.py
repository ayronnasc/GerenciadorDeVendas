from datetime import datetime
from typing import List
from uuid import UUID

from sqlalchemy import ForeignKey, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Item
from app.models.Item_Sale import Item_Sale
from app.models.registry_tables import table_registry
from app.schemas.item import ItemPublic


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

    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id'))

    item_sale: Mapped[List['Item_Sale']] = relationship(
        argument='Item_Sale',
        init=False,
        cascade='all, delete-orphan',
        lazy='selectin',
        default_factory=list,
        back_populates='sales',
    )

    @property
    def item_list(self) -> list[ItemPublic]:
        item_list = []
        for item_sale in self.item_sale:
            item_sale.item.value = item_sale.value
            item_sale.item.amount = item_sale.amount
            item_list.append(
                ItemPublic(
                    id=item_sale.item.id,
                    title=item_sale.item.title,
                    description=item_sale.item.description,
                    value=item_sale.item.value,
                    amount=item_sale.item.amount,
                    state=item_sale.item.state,
                    created_at=item_sale.item.created_at,
                    updated_at=item_sale.item.updated_at,
                )
            )
        return item_list

    def add_item(self, item: Item, amount: int = 0, value: float = 0.00):
        self.total += amount * value
        new_item_sale = Item_Sale(item=item, amount=amount, value=value)
        self.item_sale.append(new_item_sale)

    def update_item(self, item_id: int, amount: int = 0):
        for i_s in self.item_sale:
            if i_s.item_id == item_id:
                self.total -= i_s.amount * i_s.value
                i_s.amount = amount
                self.total += amount * i_s.value
                return

    async def remove_item(self, item_sale: Item_Sale, session: AsyncSession):
        for i_s in self.item_sale:
            if i_s.item_id == item_sale.item_id:
                self.total -= i_s.amount * i_s.value
                self.item_sale.remove(i_s)

                if len(self.item_sale) == 0:
                    await session.delete(self)
                    await session.commit()
                    return True

                return False
            return False
