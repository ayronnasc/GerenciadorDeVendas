from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_session
from backend.app.models.User import User
from backend.app.schemas.application import Token
from backend.app.security import (
    create_access_token,
    get_current_user,
    verify_password,
)

router = APIRouter(prefix='/auth', tags=['auth'])

Session = Annotated[AsyncSession, Depends(get_session)]
OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post('/token', response_model=Token)
async def login_for_acess_token(
    session: Session,
    form_data: OAuth2Form,
):
    user = await session.scalar(
        select(User).where(User.email == form_data.username)
    )

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorret email or password',
        )

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorret email or password',
        )

    acess_token = create_access_token({'sub': user.email})

    return {'access_token': acess_token, 'token_type': 'Bearer'}


@router.post('/refresh_token', response_model=Token)
async def refresh_token(user: Annotated[User, Depends(get_current_user)]):
    new_access_token = create_access_token(data={'sub': user.email})

    return {'access_token': new_access_token, 'token_type': 'Bearer'}
