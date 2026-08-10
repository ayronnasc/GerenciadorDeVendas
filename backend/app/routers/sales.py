from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Item, Sale, User
from backend.app.models.Item_Sale import Item_Sale
from backend.app.models.Item import ItemState
from backend.app.schemas.application import Message
from backend.app.schemas.filters import FilterSale
from backend.app.schemas.sale import (
    SaleList,
    SalePublic,
    SaleResponse,
    SaleSchema,
    SaleUpdate,
)
from backend.app.security import get_current_user, get_session

router = APIRouter(prefix='/sales', tags=['sales'])

Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', response_model=SalePublic, status_code=HTTPStatus.CREATED)
async def create_sale(sale: SaleSchema, session: Session, user: CurrentUser):

    total = 0.0

    db_sale = Sale(
        description=sale.description,
        user_id=user.id,
        total=total,
    )

    for item in sale.items:
        _item = await session.scalar(
            select(Item).where(Item.id == item.item_id)
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

        if _item.amount - item.amount == 0 :
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


@router.get('/', status_code=HTTPStatus.OK, response_model=SaleList)
async def list_items(
    user: CurrentUser,
    session: Session,
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

    return {'sales': sales.all()}


@router.patch(
    '/{sale_id}', response_model=SaleResponse, status_code=HTTPStatus.OK
)
async def update_sale(
    sale_id: int, sale: SaleUpdate, session: Session, user: CurrentUser
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
            if not item.item_id:
                raise HTTPException(
                    status_code=HTTPStatus.CONFLICT, detail='item_id is need'
                )

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


@router.delete('/{sale_id}', response_model=Message, status_code=HTTPStatus.OK)
async def delete_sale(sale_id: int, session: Session, user: CurrentUser):
    db_sale = await session.scalar(
        select(Sale).where(Sale.id == sale_id, Sale.user_id == user.id)
    )

    if not db_sale:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Sale not found'
        )

    await session.delete(db_sale)
    await session.commit()

    return {'message': 'Sale deleted with success!'}
