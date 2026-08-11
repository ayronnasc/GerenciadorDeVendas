from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.User import User
from app.schemas.application import Message
from app.schemas.user import UserPublic, UserSchema
from app.security import (
    get_current_user,
)
from app.services.users import S_create_user, S_delete_user, S_update_user

router = APIRouter(tags=['users'], prefix='/users')

Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
async def create_user(user: UserSchema, session: Session):
    return await S_create_user(user, session)


# @router.get('/', status_code=HTTPStatus.OK, response_model=UserList)
# async def read_users(
#    session: Session,
#    current_user: CurrentUser,
#    filter_users: Annotated[FilterPage, Query()],
# ):
#    users = await session.scalars(
#        select(User).limit(filter_users.limit).offset(filter_users.offset)
#    )
#    return {'users': users}


@router.put('/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
async def update_user(
    user_id: UUID,
    user: UserSchema,
    session: Session,
    current_user: CurrentUser,
):
    return await S_update_user(user_id, user, session, current_user)


@router.delete('/{user_id}', status_code=HTTPStatus.OK, response_model=Message)
async def delete_user(
    user_id: UUID,
    session: Session,
    current_user: CurrentUser,
):
    return await S_delete_user(user_id, session, current_user)
