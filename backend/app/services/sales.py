from http import HTTPStatus
from typing import Annotated

from fastapi import HTTPException, Query
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Item, Sale, User
from app.models.Item import ItemState
from app.models.Item_Sale import Item_Sale
from app.schemas.filters import FilterSale
from app.schemas.sale import SaleResponse, SaleSchema, SaleUpdate


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


async def S_get_sales(
    user: User,
    session: AsyncSession,
    sale_filter: Annotated[FilterSale, Query()],
):

    query = select(Sale).where(Sale.user_id == user.id)

    if sale_filter.total:
        query = query.filter(Sale.total == sale_filter.total)
    if sale_filter.description:
        query = query.filter(
            Sale.description.contains(sale_filter.description)
        )
    if sale_filter.greater_than:
        query = query.filter(Sale.total >= sale_filter.greater_than)

    if sale_filter.less_than:
        query = query.filter(Sale.total <= sale_filter.less_than)

    sales = await session.scalars(
        query.limit(sale_filter.limit).offset(sale_filter.offset)
    )

    result = sales.all()

    if not result:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Sale not found for this search',
        )

    return {'sales': result}


async def S_update_sale(
    sale_id: int, sale: SaleUpdate, session: AsyncSession, user: User
):
    db_sale = await session.scalar(
        select(Sale).where(Sale.id == sale_id, Sale.user_id == user.id)
    )

    if not db_sale:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Sale not found'
        )

    if sale.items:
        for item in sale.items:
            # previous item
            p_item = await session.scalar(
                select(Item_Sale).where(Item_Sale.item_id == item.item_id)
            )
            if not p_item:
                # new item in sale
                new_item = await session.scalar(
                    select(Item).where(Item.id == item.item_id)
                )
                if not new_item:
                    raise HTTPException(
                        status_code=HTTPStatus.NOT_FOUND,
                        detail='Item not found',
                    )

                db_sale.add_item(
                    new_item, amount=item.amount, value=new_item.value
                )
                continue

            if item.delete:
                sale_deleted = await db_sale.remove_item(p_item, session)

                if sale_deleted:
                    return SaleResponse(
                        message='Sale has been deleted for does '
                        'not exists items inside'
                    )
                else:
                    continue

            db_sale.update_item(p_item.item_id, item.amount)

    if sale.description:
        db_sale.description = sale.description

    session.add(db_sale)
    await session.commit()
    await session.refresh(db_sale)

    return SaleResponse(sale=db_sale)
