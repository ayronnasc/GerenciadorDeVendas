from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.schemas.application import Message
from app.schemas.filters import FilterItem
from app.schemas.item import ItemList, ItemPublic, ItemSchema, ItemUpdate
from app.security import get_current_user, get_session
from app.services.items import add_item, get_items, remove_item, uptodate_item

router = APIRouter(prefix='/items', tags=['items'])

Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', response_model=ItemPublic, status_code=HTTPStatus.CREATED)
async def create_Item(item: ItemSchema, session: Session, user: CurrentUser):
    return await add_item(item, session, user)


@router.get('/', status_code=HTTPStatus.OK, response_model=ItemList)
async def list_items(
    user: CurrentUser,
    session: Session,
    item_filter: Annotated[FilterItem, Query()],
):
    return await get_items(user, session, item_filter)


@router.patch('/{item_id}', response_model=ItemPublic)
async def patch_item(
    item_id: int, session: Session, user: CurrentUser, item: ItemUpdate
):
    return await uptodate_item(item_id, item, session, user)


@router.delete('/{item_id}', status_code=HTTPStatus.OK, response_model=Message)
async def delete_item(
    item_id: int,
    user: CurrentUser,
    session: Session,
):
    return await remove_item(item_id, session, user)
