from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Item, User
from app.schemas.application import Message
from app.schemas.filters import FilterItem
from app.schemas.item import ItemList, ItemPublic, ItemSchema, ItemUpdate
from app.security import get_current_user, get_session

router = APIRouter(prefix='/items', tags=['items'])

Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', response_model=ItemPublic, status_code=HTTPStatus.CREATED)
async def create_Item(item: ItemSchema, session: Session, user: CurrentUser):

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


@router.get('/', status_code=HTTPStatus.OK, response_model=ItemList)
async def list_items(
    user: CurrentUser,
    session: Session,
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

    return {'items': items.all()}


@router.patch('/{item_id}', response_model=ItemPublic)
async def patch_item(
    item_id: int, session: Session, user: CurrentUser, item: ItemUpdate
):

    db_item = await session.scalar(
        select(Item).where(Item.user_id == user.id, Item.id == item_id)
    )

    if not db_item:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Item not found'
        )

    for key, value in item.model_dump(exclude_unset=True).items():
        setattr(db_item, key, value)

    session.add(db_item)
    await session.commit()
    await session.refresh(db_item)

    return db_item


@router.delete('/{item_id}', status_code=HTTPStatus.OK, response_model=Message)
async def delete_item(
    item_id: int,
    user: CurrentUser,
    session: Session,
):
    item = await session.scalar(
        select(Item).where(Item.user_id == user.id, Item.id == item_id)
    )

    if not item:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Item not found'
        )

    await session.delete(item)
    await session.commit()

    return {'message': 'Item has been deleted sucessfully'}
