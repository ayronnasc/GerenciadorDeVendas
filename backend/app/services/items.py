from http import HTTPStatus
from typing import Annotated

from fastapi import HTTPException, Query
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Item, User
from app.models.Item import ItemState
from app.schemas.filters import FilterItem
from app.schemas.item import ItemSchema, ItemUpdate


async def add_item(item: ItemSchema, session: AsyncSession, user: User):

    db_item = Item(
        title=item.title,
        description=item.description,
        value=item.value,
        amount=item.amount,
        state=item.state,
        user_id=user.id,
    )

    session.add(db_item)
    await session.commit()
    await session.refresh(db_item)

    return db_item


async def get_items(
    user: User,
    session: AsyncSession,
    item_filter: Annotated[FilterItem, Query()],
):
    query = select(Item).where(Item.user_id == user.id)

    if item_filter.title:
        query = query.filter(Item.title.contains(item_filter.title))
    if item_filter.description:
        query = query.filter(
            Item.description.contains(item_filter.description)
        )
    if item_filter.value:
        query = query.filter(Item.value == item_filter.value)
    if item_filter.amount:
        query = query.filter(Item.amount == item_filter.amount)
    if item_filter.state:
        query = query.filter(Item.state == item_filter.state)
    items = await session.scalars(
        query.limit(item_filter.limit).offset(item_filter.offset)
    )

    result = items.all()

    if not result:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Not found items for this search',
        )

    return {'items': result}


async def remove_item(item_id: int, session: AsyncSession, user: User):

    item_exception = HTTPException(
        status_code=HTTPStatus.NOT_FOUND, detail='Item not found'
    )

    response = await session.execute(
        delete(Item).where(Item.id == item_id, Item.user_id == user.id)
    )
    await session.commit()

    if response.rowcount == 0:
        raise item_exception

    return {'message': 'Item has been deleted sucessfully'}


async def uptodate_item(
    item_id: int, item_data: ItemUpdate, session: AsyncSession, user: User
):

    item_exception = HTTPException(
        status_code=HTTPStatus.NOT_FOUND, detail='Item not found'
    )

    item_data = item_data.model_dump(exclude_unset=True)
    item = None

    if item_data:
        item = await session.execute(
            update(Item)
            .where(Item.id == item_id, Item.user_id == user.id)
            .values(**item_data)
            .returning(Item)
        )

        if 'amount' in item_data:
            if item_data['amount'] > 0 and 'state' not in item_data:
                item = await session.execute(
                    update(Item)
                    .where(Item.id == item_id, Item.user_id == user.id)
                    .values(state=ItemState.available)
                    .returning(Item)
                )

        await session.commit()

        result = item.scalar_one_or_none()

        if not result:
            raise item_exception

        return result

    raise HTTPException(
        status_code=HTTPStatus.UNPROCESSABLE_CONTENT,
        detail='Item data is need to update',
    )
