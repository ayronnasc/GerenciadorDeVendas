from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Item, Sale, User
from app.models.Item import ItemState
from app.models.Item_Sale import Item_Sale
from app.schemas.sale import SaleSchema


async def S_delete_sale(sale_id: int, session: AsyncSession, user: User):
    delete_exception = HTTPException(
        status_code=HTTPStatus.NOT_FOUND, detail='Sale not found'
    )

    result = await session.execute(
        delete(Sale).where(Sale.id == sale_id, Sale.user_id == user.id)
    )
    await session.commit()

    if result.rowcount == 0:
        raise delete_exception

    return {'message': 'Sale deleted with success!'}


async def S_create_sale(sale: SaleSchema, session: AsyncSession, user: User):
    total = 0.0

    db_sale = Sale(
        description=sale.description,
        user_id=user.id,
        total=total,
    )

    for item in sale.items:
        _item = await session.scalar(
            select(Item).where(
                Item.id == item.item_id, Item.user_id == user.id
            )
        )

        if not _item:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='the item does not exists',
            )

        if item.amount > _item.amount or _item.amount == 0:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='This amount is not available for this item',
            )

        if _item.amount - item.amount == 0:
            await session.execute(
                update(Item)
                .where(Item.id == item.item_id)
                .values(amount=0, state=ItemState.unavailable)
            )
        else:
            await session.execute(
                update(Item)
                .where(Item.id == item.item_id)
                .values(amount=Item.amount - item.amount)
            )

        await session.commit()

        db_sale.add_item(_item, amount=item.amount, value=_item.value)

    session.add(db_sale)
    await session.commit()
    db_sale_reloaded = await session.scalar(
        select(Sale)
        .options(selectinload(Sale.item_sale).selectinload(Item_Sale.item))
        .where(Sale.id == db_sale.id)
    )

    return db_sale_reloaded
